#!/usr/bin/env python3
"""
Cliente de prueba para el sistema de scraping distribuido.
Permite probar ambos modos: asíncrono con task_id y síncrono.
"""

import requests
import argparse
import time
import json
from typing import Dict


def scrape_async(server_url: str, target_url: str) -> str:
    """
    Inicia un scraping asíncrono y devuelve el task_id.
    
    Args:
        server_url: URL del servidor (ej: http://localhost:8000)
        target_url: URL a scrapear
    
    Returns:
        task_id de la tarea creada
    """
    endpoint = f"{server_url}/scrape"
    
    print(f"Enviando request para scrappear la url: {target_url}")

    response = requests.post(
        endpoint,
        json={'url': target_url},
        timeout=10
    )
    
    if response.status_code == 202:
        data = response.json()
        task_id = data['task_id']
        print(f"Tarea creada, ID: {task_id}")
        print(f"Estado: {data['status']}")
        return task_id
    else:
        print(f"Error al crear tarea: {response.text}")
        return None


def check_status(server_url: str, task_id: str) -> Dict:
    """
    Consulta el estado de una tarea.
    
    Args:
        server_url: URL del servidor
        task_id: ID de la tarea
    
    Returns:
        Dict con información de estado
    """
    endpoint = f"{server_url}/status/{task_id}"
    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"ERROR {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR. No se pudo consultar estado: {e}")
        return None

def get_result(server_url: str, task_id: str) -> Dict:
    """
    Obtiene el resultado de una tarea completada.
    
    Args:
        server_url: URL del servidor
        task_id: ID de la tarea
    
    Returns:
        Dict con el resultado completo
    """
    endpoint = f"{server_url}/result/{task_id}"

    try:
        response = requests.get(endpoint, timeout=10)
        if response.status_code == 200:
            print("Resultado obtenido exitosamente ✅")
            return response.json()
        else:
            print(f"ERROR {response.text}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR. No se pudo obtener resultado: {e}")
        return None
    
def wait_for_completion(server_url: str, task_id: str, max_wait: int = 120) -> Dict: 

    print(f"Esperando completación de tarea {task_id}...") 

    start_time = time.time() 

    while time.time() - start_time < max_wait: 
        status = check_status(server_url, task_id) 

        if not status: 
            return None 
        
        current_status = status['status'] 
        print(f"Estado: {current_status}") 

        if current_status == 'completed': 
            print("Tarea completada") 
            return get_result(server_url, task_id) 
        elif current_status == 'failed': 
            print(f"ERROR. Tarea falló: {status.get('error', 'Error desconocido')}") 
            return None  
        
        time.sleep(2) 
        
    print("Timeout esperando completación") 
    return None


def print_result(result: Dict):
    """
    Imprime el resultado de forma legible.
    
    Args:
        result: Dict con el resultado del scraping
    """
    if not result:
        return
    
    print("\n" + "=" * 80)
    print("RESULTADO DEL SCRAPING")
    print("=" * 80)
    
    print(f"\n URL: {result.get('url')}")
    print(f" Timestamp: {result.get('timestamp')}")
    print(f" Desde caché: {result.get('from_cache', False)}")
    
    scraping = result.get('scraping_data', {})
    print(f"\n SCRAPING DATA:")
    print(f"   Título: {scraping.get('title', 'N/A')}")
    print(f"   Cantidad de Enlaces encontrados: {len(scraping.get('links', []))}")
    print(f"   Cantidad de Imágenes: {scraping.get('images_count', 0)}")
    
    structure = scraping.get('structure', {})
    print(f"\n  ESTRUCTURA:")
    for h_tag, count in structure.items():
        if count > 0:
            print(f"   {h_tag.upper()}: {count}")
    
    meta = scraping.get('meta_tags', {})
    print(f"\n  META TAGS:")
    print(f"   Descripción: {meta.get('description', 'N/A')}")
    print(f"   Keywords: {', '.join(meta.get('keywords', []))}")
    
    processing = result.get('processing_data', {})
    print(f"\n  PROCESSING DATA:")
    
    if processing.get('screenshot'):
        screenshot_size = len(processing['screenshot'])
        print(f"   Screenshot: {screenshot_size} bytes (base64)")
    
    if processing.get('performance'):
        performance = processing['performance']
        
        print(f"\n RENDIMIENTO:")
        print(f"   Tiempo de carga: {performance.get('load_time_ms', 'N/A')} ms")
        print(f"   Tamaño total: {performance.get('total_size_kb', 'N/A')} KB")
        print(f"   Número de requests: {performance.get('num_requests', 'N/A')}")
    
    if processing.get('thumbnails'):
        thumbnails = processing['thumbnails']
        successful = sum(1 for t in thumbnails if t.get('status') == 'success')
        print(f"\n  THUMBNAILS: {successful}/{len(thumbnails)} procesados exitosamente")
    
    print("\n" + "=" * 80)


def save_result_to_file(result: Dict, filename: str):
    """
    Guarda el resultado en un archivo JSON.
    
    Args:
        result: Dict con el resultado
        filename: Nombre del archivo
    """
    if not filename.endswith('.json'):
        filename = f"{filename}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Resultado guardado en {filename}")


def main():
    """Función principal del cliente"""
    parser = argparse.ArgumentParser(
        description='Cliente para sistema de scraping distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        '-s', '--server',
        required=True,
        help='URL del servidor'
    )
    
    parser.add_argument(
        '-u', '--url',
        required=True,
        help='URL a scrapear'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Guardar resultado en archivo JSON'
    )
    
    args = parser.parse_args()

    
    print("=" * 60)
    print("CLIENTE DE SCRAPING DISTRIBUIDO")
    print("=" * 60)
    print(f"Servidor: {args.server}")
    print(f"URL objetivo: {args.url}")
    print("=" * 60 + "\n")
    

    result = None

    try: 
        task_id = scrape_async(args.server, args.url) 
        
        if task_id: 
            result = wait_for_completion(args.server, task_id) 
        else: 
            print("ERROR. No se pudo crear la tarea en el servidor") 
                
        if result: 
            print_result(result)                 
            if args.output: 
                save_result_to_file(result, args.output)
            else:
                save_opt = input("\n¿Desea guardar el resultado en un archivo? (s/n): ").strip().lower()
                if save_opt == 's':
                    save_result_to_file(result, "json_response")

    except KeyboardInterrupt:
        print("\nERROR. Interrumpido por usuario")
    
    except requests.exceptions.ConnectionError:
        print(f"ERROR. No se pudo conectar al servidor {args.server}")
        print("Verifique que el servidor esté corriendo")
    
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == '__main__':
    main()