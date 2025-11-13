#!/usr/bin/env python3
"""
Servidor de Procesamiento Distribuido con Multiprocessing
Parte B del TP2 - Computación II

Este servidor maneja tareas CPU-intensive usando un pool de procesos.
Escucha conexiones TCP y procesa solicitudes de:
- Generación de screenshots
- Análisis de rendimiento
- Procesamiento de imágenes
"""

import socketserver
import argparse
import signal
import sys
from multiprocessing import Pool, cpu_count
from typing import Dict, Any

# Importar módulos propios
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import extract_and_process_images
from common.protocol import send_message, receive_message
from common.errors import ProcessingError


# Pool global de procesos
process_pool = None


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """
    Handler para procesar requests del Servidor A.
    Cada request se procesa en un proceso separado del pool.
    """
    
    def handle(self):
        """Maneja una conexión entrante"""
        client_addr = self.client_address
        print(f"Nueva conexión desde {client_addr}")

        self.request.settimeout(95)
        
        try:
            # Recibir mensaje del Servidor A
            request = receive_message(self.request)
            print(f"Request recibido")
            
            # Procesar según tipo de tarea
            response = self._process_request(request)
            
            # Enviar respuesta
            send_message(self.request, response)
            print(f"Respuesta enviada a {client_addr}")
        
        except Exception as e:
            error_response = {
                'status': 'error',
                'error': str(e)
            }
            try:
                send_message(self.request, error_response)
            except:
                pass
            print(f"Error procesando request de {client_addr}: {e}")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa el request usando el pool de procesos.
        
        Args:
            request: Dict con 'task_type', 'url' y otros parámetros
        
        Returns:
            Dict con resultados del procesamiento
        """
        task_type = request.get('task_type')
        url = request.get('url')
        
        if not url:
            raise ValueError("ERROR, URL no proporcionada en el request")
        
        print(f"INICIANDO TAREA para {url}")
        
        try:
            # Procesamiento completo: todas las tareas en paralelo
            result = self._handle_full_processing(request)
        
            print(f"TAREA COMPLETADA para {url}")
            return result
        
        except Exception as e:
            print(f"Error en tarea: {e}")
            raise ProcessingError(f"Error procesando: {e}")
    
    def _handle_full_processing(self, request: Dict) -> Dict:
        """
        Ejecuta todas las tareas en paralelo usando el pool.
        """
        url = request['url']
        
        # Lanzar todas las tareas en paralelo
        screenshot_task = process_pool.apply_async(generate_screenshot, (url,))
        performance_task = process_pool.apply_async(analyze_performance, (url,))
        images_task = process_pool.apply_async(extract_and_process_images, (url,))
        
        # Esperar resultados con timeout
        try:
            screenshot = screenshot_task.get(timeout=60)
        except Exception as e:
            screenshot = f"Error al realizar el screenshot. ERROR: {e}"
            print(f"ERROR, screenshot falló: {e}, continua la ejecucion...")
        
        try:
            performance = performance_task.get(timeout=60)
        except Exception as e:
            performance = f"Error al analizar el rendimiento. ERROR: {e}"
            print(f"[ERROR, Análisis de rendimiento falló: {e}, continua la ejecucion...")
        
        try:
            thumbnails = images_task.get(timeout=90)
        except Exception as e:
            thumbnails = f"Error al procesar imágenes. ERROR: {e}"
            print(f"ERROR, Procesamiento de imágenes falló: {e}, continua la ejecucion...")
        
        return {
            'screenshot': screenshot,
            'performance': performance,
            'thumbnails': thumbnails
        }
    


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que maneja cada conexión en un thread separado.
    Permite múltiples clientes concurrentes.
    """
    allow_reuse_address = True
    daemon_threads = True


def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección IP de escucha (IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=3,
        help=f'Número de procesos en el pool (default: 3)'
    )
    
    return parser.parse_args()


def signal_handler(sig, frame):
    """Maneja señales de terminación"""
    print("\nSeñal de terminación recibida. Cerrando servidor...")
    
    if process_pool:
        print("Cerrando pool de procesos...")
        process_pool.close()
        process_pool.terminate()
        process_pool.join()
    
    sys.exit(0)


def main():
    """Función principal del servidor"""
    global process_pool
    
    # Parsear argumentos
    args = parse_arguments()
    
    print("=" * 60)
    print("SERVIDOR DE PROCESAMIENTO DISTRIBUIDO")
    print("=" * 60)
    print(f"Dirección: {args.ip}")
    print(f"Puerto: {args.port}")
    print(f"Procesos en pool: {args.processes}")
    print("=" * 60)
    
    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Inicializar pool de procesos
        print(f"Inicializando pool con {args.processes} procesos...")
        process_pool = Pool(processes=args.processes)
        print("Pool de procesos inicializado")
        
        # Crear y arrancar servidor
        server = ThreadedTCPServer((args.ip, args.port), ProcessingRequestHandler)
        print(f"Servidor escuchando en {args.ip}:{args.port}")
        print("Esperando conexiones... (Ctrl+C para detener)")
        
        # Servir indefinidamente
        server.serve_forever()
    
    except OSError as e:
        print(f"ERROR, No se pudo iniciar el servidor: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)
    
    finally:
        if process_pool:
            process_pool.close()
            process_pool.terminate()
            process_pool.join()
        print('\n')
        print('CIERRE DE SERVIDOR COMPLETADO')


if __name__ == '__main__':
    main()