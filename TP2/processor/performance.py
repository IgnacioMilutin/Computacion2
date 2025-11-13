import time
from urllib.parse import urljoin
import requests
from typing import Dict
from bs4 import BeautifulSoup
from common.errors import ProcessingError


# Analiza el rendimiento de la página
def analyze_performance(url: str, timeout: int = 30) -> Dict[str, any]:
    max_size_html = 5 * 1024 * 1024  # 5MB
    retries=3
    delay=1

    for attempt in range(retries):
        try:
            start_time = time.time()
            
            response = requests.get(
                url,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 Web Scraper Bot'}
            )
            response.raise_for_status()

            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000 
            
            html_size = len(response.content)

            if html_size > max_size_html:
                raise ProcessingError(
                    f"La página {url} excede el tamaño máximo permitido de {max_size_html / (1024*1024)} MB"
                )
            
            html = BeautifulSoup(response.text, 'lxml')
            
            resources = analyze_resources(html,url)
            
            total_size = html_size + resources['total_size']
            
            return {
                'load_time_ms': round(load_time, 2),
                'total_size_kb': round(total_size / 1024, 3),
                'num_requests': 1 + resources['count'],
            }
        
        except requests.RequestException as e:
            if attempt < retries - 1:
                print(f"[WARN] Error accediendo a {url} (intento {attempt+1}/{retries}), reintentando...")
                time.sleep(delay)
                continue
            raise ProcessingError(f"Error al analizar rendimiento de {url}, no se logro acceder al dominio. Error: {e}")
        
        except Exception as e:
            raise ProcessingError(f"Error inesperado al analizar rendimiento: {e}")


# Analiza los recursos de la página
def analyze_resources(html: BeautifulSoup, base_url: str) -> Dict[str, any]:
    resources = {
        'count': 0,
        'total_size': 0
    }

    resource_urls = set()

    for tag in html.find_all('script', src=True):
        resource_urls.add(urljoin(base_url, tag['src']))

    for tag in html.find_all('link', rel='stylesheet', href=True):
        resource_urls.add(urljoin(base_url, tag['href']))

    for tag in html.find_all('img', src=True):
        resource_urls.add(urljoin(base_url, tag['src']))

    for tag in html.find_all('link', href=True):
        href = tag['href'].lower()
        if 'font' in href or tag.get('type', '').startswith('font/'):
            resource_urls.add(urljoin(base_url, tag['href']))

    for res_url in resource_urls:
        resources['count'] += 1
        try:
            head = requests.head(res_url, timeout=5, allow_redirects=True)
            size = int(head.headers.get('Content-Length', 0))

            if size == 0 or size==None:
                get_resp = requests.get(res_url, timeout=10, stream=True)
                size = 0
                for chunk in get_resp.iter_content(chunk_size=51200):
                    size += len(chunk)
                    if size > 5 * 1024 * 1024:
                        break

            resources['total_size'] += size

        except Exception:
            continue

    return resources