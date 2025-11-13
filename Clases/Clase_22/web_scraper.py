from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time

def descargar_url(url):
    """Descarga una URL y retorna estadísticas"""
    try:
        inicio = time.time()
        response = requests.get(url, timeout=10)
        duracion = time.time() - inicio
        
        return {
            "url": url,
            "status": response.status_code,
            "tamaño": len(response.content),
            "duracion": duracion,
            "exito": response.status_code == 200
        }
    
    except Exception as e:
        return {
            "url": url,
            "error": str(e),
            "exito": False
        }

def scraper_secuencial(urls):
    """Versión secuencial"""
    inicio = time.time()
    resultados = [descargar_url(url) for url in urls]
    return resultados, time.time() - inicio

def scraper_concurrente(urls, max_workers=10):
    """Versión con threads"""
    inicio = time.time()
    resultados = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Crear futures
        future_to_url = {
            executor.submit(descargar_url, url): url 
            for url in urls
        }
        
        # Procesar según terminan
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                resultado = future.result()
                resultados.append(resultado)
                
                status = "✓" if resultado.get("exito") else "✗"
                print(f"{status} {url[:50]}")
                
            except Exception as e:
                print(f"✗ {url}: {e}")
    
    return resultados, time.time() - inicio

# Uso
if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://docs.python.org",
        "https://pypi.org",
        # ... más URLs
    ] * 10  # 30 URLs total
    
    print("=== SECUENCIAL ===")
    resultados_seq, tiempo_seq = scraper_secuencial(urls[:5])
    print(f"Tiempo: {tiempo_seq:.2f}s\n")
    
    print("=== CONCURRENTE (10 threads) ===")
    resultados_con, tiempo_con = scraper_concurrente(urls[:5], max_workers=10)
    print(f"Tiempo: {tiempo_con:.2f}s")
    print(f"Speedup: {tiempo_seq/tiempo_con:.2f}x")
    
    # Estadísticas
    exitosos = sum(1 for r in resultados_con if r.get("exito"))
    print(f"\n📊 Éxito: {exitosos}/{len(resultados_con)}")