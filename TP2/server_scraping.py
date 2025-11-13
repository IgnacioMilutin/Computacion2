#!/usr/bin/env python3
"""
Servidor de Scraping Web Asíncrono
Parte A del TP2 - Computación II

Servidor HTTP asíncrono que maneja scraping de páginas web.
Incluye:
- Sistema de cola con IDs de tarea (Bonus Track 1)
- Rate Limiting y Caché (Bonus Track 2)
- Comunicación con Servidor de Procesamiento
- Soporte IPv4/IPv6
"""

import asyncio
import argparse
from concurrent.futures import ProcessPoolExecutor
import signal
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict
from aiohttp import web
import json
import signal
import sys

# Importar módulos propios
from scraper import parse_html, extract_metadata, fetch_url
from common.protocol import async_send_message, async_receive_message
from common.errors import ScrapingError, RateLimitError
from common.serialization import serialize_data


# ==================== SISTEMA DE CACHÉ ====================

class Cache:
    """
    Sistema de caché con TTL (Time To Live).
    Bonus Track 2: Almacena resultados de scraping recientes.
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[Dict]:
        """Obtiene un valor del caché si no ha expirado"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                print(f"[CACHE HIT] {key}")
                return entry['data']
            else:
                # Expirado, eliminar
                del self.cache[key]
                print(f"[CACHE EXPIRED] {key}")
        return None
    
    def set(self, key: str, data: Dict):
        """Almacena un valor en el caché con timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        print(f"[CACHE SET] {key}")
    
    def clear(self):
        """Limpia todo el caché"""
        self.cache.clear()
        print("Cache limpiado")


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Rate limiter por dominio.
    Bonus Track 2: Limita requests por dominio para evitar sobrecarga.
    """
    
    def __init__(self, max_requests_per_minute: int = 10):
        self.requests = defaultdict(list)  # domain -> [timestamps]
        self.max_rpm = max_requests_per_minute
        self.window = 60  # 1 minuto en segundos
    
    def can_request(self, domain: str) -> bool:
        """Verifica si se puede hacer un request al dominio"""
        now = time.time()
        
        # Limpiar timestamps antiguos
        self.requests[domain] = [
            ts for ts in self.requests[domain]
            if now - ts < self.window
        ]
        
        # Verificar límite
        return len(self.requests[domain]) < self.max_rpm
    
    def record_request(self, domain: str):
        """Registra un request al dominio"""
        self.requests[domain].append(time.time())
    
    async def wait_if_needed(self, domain: str):
        """Espera si es necesario para respetar rate limit"""
        if not self.can_request(domain):
            # Calcular cuánto esperar
            oldest = min(self.requests[domain])
            wait_time = self.window - (time.time() - oldest) + 1
            print(f"[RATE LIMIT] Esperando {wait_time:.1f}s para {domain}")
            await asyncio.sleep(wait_time)
        
        self.record_request(domain)


# ==================== SISTEMA DE TAREAS ====================

class TaskManager:
    """
    Gestor de tareas asíncronas con IDs.
    Bonus Track 1: Sistema de cola con task_id.
    """
    
    def __init__(self):
        self.tasks = {}  # task_id -> task_info
    
    def create_task(self, url: str) -> str:
        """Crea una nueva tarea y devuelve su ID"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            'id': task_id,
            'url': url,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'result': None,
            'error': None
        }
        print(f"TAREA CREADA con ID:{task_id} para {url}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Obtiene información de una tarea"""
        return self.tasks.get(task_id)
    
    def update_status(self, task_id: str, status: str):
        """Actualiza el estado de una tarea"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = status
            print(f"Tarea {task_id}: {status}")
    
    def set_result(self, task_id: str, result: Dict):
        """Establece el resultado de una tarea completada"""
        if task_id in self.tasks:
            self.tasks[task_id]['result'] = result
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
    
    def set_error(self, task_id: str, error: str):
        """Establece un error en una tarea"""
        if task_id in self.tasks:
            self.tasks[task_id]['error'] = error
            self.tasks[task_id]['status'] = 'failed'


# ==================== GLOBALS ====================

cache = None
rate_limiter = None
task_manager = None
processor_host = None
processor_port = None
process_pool = None


# ==================== HANDLERS HTTP ====================

async def handle_scrape(request):
    """
    Handler para POST /scrape
    Inicia un scraping asíncrono y devuelve task_id inmediatamente.
    """
    try:
        data = await request.json()
        url = data.get('url')
        
        if not url:
            return web.json_response(
                {'error': 'URL requerida'},
                status=400
            )
        
        # Crear tarea
        task_id = task_manager.create_task(url)
        
        # Lanzar procesamiento asíncrono (fire and forget)
        task = asyncio.create_task(process_scraping_task(request.app, task_id, url))
        

        request.app['active_tasks'].add(task)
        
        return web.json_response({
            'task_id': task_id,
            'status': 'pending',
            'message': 'Tarea creada. Utiliza /status/{task_id} para consultar estado.'
        }, status=202)
    
    except Exception as e:
        return web.json_response(
            {'error': str(e)},
            status=500
        )


async def handle_status(request):
    """
    Handler para GET /status/{task_id}
    Devuelve el estado actual de una tarea.
    """
    task_id = request.match_info['task_id']
    task = task_manager.get_task(task_id)
    
    if not task:
        return web.json_response(
            {'error': 'Tarea no encontrada'},
            status=404
        )
    
    response = {
        'task_id': task['id'],
        'url': task['url'],
        'status': task['status'],
        'created_at': task['created_at']
    }
    
    if task['status'] == 'failed':
        response['error'] = task['error']
    
    return web.json_response(response)


async def handle_result(request):
    """
    Handler para GET /result/{task_id}
    Devuelve el resultado de una tarea completada.
    """
    task_id = request.match_info['task_id']
    task = task_manager.get_task(task_id)
    
    if not task:
        return web.json_response(
            {'error': 'Tarea no encontrada'},
            status=404
        )
    
    if task['status'] != 'completed':
        return web.json_response({
            'error': f"Tarea no completada. Estado actual: {task['status']}",
            'status': task['status']
        }, status=400)
    
    return web.json_response(task['result'])


# ==================== LÓGICA DE SCRAPING ====================

async def process_scraping_task(app, task_id: str, url: str):
    """
    Procesa una tarea de scraping de forma asíncrona.
    Esta función se ejecuta en background.
    """
    try:
        task_manager.update_status(task_id, 'scraping')
        result = await full_scraping_process(url)
        task_manager.set_result(task_id, result)
    
    except Exception as e:
        task_manager.set_error(task_id, str(e))
        print(f"Tarea {task_id} falló: {e}")

    finally:
        app['active_tasks'].discard(asyncio.current_task())


async def full_scraping_process(url: str) -> Dict:
    """
    Proceso completo de scraping + procesamiento.
    
    1. Verifica caché
    2. Aplica rate limiting
    3. Hace scraping del HTML
    4. Se comunica con Servidor B para procesamiento
    5. Consolida y devuelve resultado
    """
    from urllib.parse import urlparse
    
    # Extraer dominio para rate limiting
    domain = urlparse(url).netloc
    
    # 1. Verificar caché
    # cached_result = cache.get(url)
    # if cached_result:
    #     cached_result['from_cache'] = True
    #     return cached_result
    
    # 2. Rate limiting
    await rate_limiter.wait_if_needed(domain)
    
    # 3. Scraping HTML
    print(f"Iniciando scraping de {url}")
    fetch_result = await fetch_url(url, timeout=30)
    html_content = fetch_result['html']
    url_final = fetch_result['url_final']

    global process_pool
    
    loop = asyncio.get_event_loop()
    
    # Crear ProcessPoolExecutor para tareas CPU-bound
    scraping_data, metadata, processing_data = await asyncio.gather(
        loop.run_in_executor(process_pool, parse_html, html_content, url_final),
        loop.run_in_executor(process_pool, extract_metadata, html_content),
        communicate_with_processor(url),
        return_exceptions=True
    )
    
    print(f"Todas las tareas completadas")
    
    # Verificar si hubo errores en alguna tarea
    if isinstance(scraping_data, Exception):
        print(f"Error en parse_html: {scraping_data}")
        scraping_data = {'error': str(scraping_data)}
    
    if isinstance(metadata, Exception):
        print(f"Error en extract_metadata: {metadata}")
        metadata = {}
    
    if isinstance(processing_data, Exception):
        print(f"Error en Servidor B: {processing_data}")
        processing_data = {'status': 'error', 'error': str(processing_data)}
    
    # Consolidar metadata en scraping_data
    scraping_data['meta_tags'] = metadata
    
    # 5. Consolidar resultado
    result = {
        'url': url,
        'timestamp': datetime.now().isoformat(),
        'scraping_data': scraping_data,
        'processing_data': processing_data,
        'status': 'success',
        'from_cache': False
    }
    
    # Guardar en caché
    # cache.set(url, result)
    
    return result


async def communicate_with_processor(url: str) -> Dict:
    """
    Se comunica con el Servidor B para procesamiento.
    Usa sockets TCP asíncronos.
    """
    try:
        # Conectar al servidor de procesamiento
        reader, writer = await asyncio.open_connection(
            processor_host,
            processor_port
        )
        
        # Preparar request
        request = {
            'url': url,
        }

        print(f"Enviando URL '{url}' al Servidor B")
        
        # Enviar request
        await async_send_message(writer, request)
        
        # Recibir respuesta
        response = await asyncio.wait_for(
            async_receive_message(reader),
            timeout=120  # 2 minutos de timeout
        )
        
        # Cerrar conexión
        writer.close()
        await writer.wait_closed()
        
        print(f"Respuesta recibida del Servidor B")
        return response
    
    except asyncio.TimeoutError:
        print("ERROR: Timeout al comunicarse con servidor de procesamiento")
        return {
            'status': 'error',
            'error': 'Timeout en procesamiento'
        }
    
    except Exception as e:
        print(f"Error al comunicarse con el servidor B: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


# ==================== CONFIGURACIÓN Y MAIN ====================

def parse_arguments():
    """Parsea argumentos CLI"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    parser.add_argument(
        '--processor-host',
        default='localhost',
        help='Host del servidor de procesamiento (default: localhost)'
    )
    
    parser.add_argument(
        '--processor-port',
        type=int,
        default=9001,
        help='Puerto del servidor de procesamiento (default: 9001)'
    )
    
    return parser.parse_args()


async def init_app(args):
    """Inicializa la aplicación web"""
    global cache, rate_limiter, task_manager, processor_host, processor_port, process_pool
    
    # Inicializar sistemas
    cache = Cache(ttl_seconds=3600)
    rate_limiter = RateLimiter(max_requests_per_minute=15)
    task_manager = TaskManager()
    processor_host = args.processor_host
    processor_port = args.processor_port
    process_pool = ProcessPoolExecutor(max_workers=args.workers)
    
    # Crear app
    app = web.Application()
    
    # Configurar rutas
    app.router.add_post('/scrape', handle_scrape)
    app.router.add_get('/status/{task_id}', handle_status)
    app.router.add_get('/result/{task_id}', handle_result)

    app['active_tasks'] = set()

    app.on_cleanup.append(on_cleanup)
    
    print('SERVIDOR INICIALIZADO. Listo para recibir requests.')
    return app


async def on_cleanup(app):
    print("Cerrando recursos y tareas...")

    tasks = list(app['active_tasks'])

    if tasks:
        print(f"Cancelando {len(tasks)} tareas en ejecución...")
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        print("Todas las tareas canceladas o finalizadas.")
    
    global process_pool, cache
    if process_pool:
        process_pool.shutdown(wait=True)
        print("Pool cerrado correctamente.")
    
    if cache:
        cache.clear()
        print("Caché limpiado.")

    print("Limpieza de recursos finalizada.")

def main():
    """Función principal"""
    args = parse_arguments()
    
    print("=" * 60)
    print("SERVIDOR DE SCRAPING WEB ASÍNCRONO - TP2 Computación II")
    print("=" * 60)
    print(f"Servidor HTTP: {args.ip}:{args.port}")
    print(f"Servidor Procesamiento: {args.processor_host}:{args.processor_port}")
    print(f"Workers: {args.workers}")
    print(f"Cache TTL: 1 hora")
    print(f"Rate Limit: 15 req/min por dominio")
    print("=" * 60)
    print("\nEndpoints disponibles:")
    print("  POST /scrape              - Crear tarea de scraping (devuelve task_id)")
    print("  GET  /status/{task_id}    - Consultar estado de tarea")
    print("  GET  /result/{task_id}    - Obtener resultado de tarea")
    print("=" * 60)
    print("\nIniciando servidor...")

    # Iniciar servidor
    try:
        web.run_app(
            init_app(args),
            host=args.ip,
            port=args.port,
            print=lambda x: None  # Suprimir logs de aiohttp
        )

    except KeyboardInterrupt:
        print('Interrupcion de manual detectada')
    except Exception as e:
        print(f'Error inesperado: {e}')

    finally:
        print('\n')
        print('\nCIERRE DE SERVIDOR COMPLETADO')
        sys.stdout.flush()

if __name__ == '__main__':
    main()