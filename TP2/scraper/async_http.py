import aiohttp
import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
from common.errors import ScrapingError, InvalidURLError


# Realiza un fetch de la URL dada
async def fetch_url(url: str, timeout: int = 30, retries: int = 3) -> Dict[str, any]:

    if not _is_valid_url(url):
        raise InvalidURLError(f"URL inválida: {url}")
    
    last_exception = None
    
    for attempt in range(retries):
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                async with session.get(
                    url,
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0 Web Scraper Bot'}
                ) as response:
                    html = await response.text()
                    
                    return {
                        'html': html,
                        'status': response.status,
                        'headers': dict(response.headers),
                        'url_final': str(response.url),
                        'content_type': response.headers.get('Content-Type', '')
                    }
        
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_exception = e
            if attempt < retries:
                    print("Reintentando en 1 segundo...")
                    await asyncio.sleep(1)

        except Exception as e:
            raise ScrapingError(f"Error inesperado al acceder a {url}: {e}")
        
    raise ScrapingError(f"No se pudo acceder a {url} tras {retries} intentos. ERROR: {last_exception}")


# Valida y corrige formato de la URL
def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False


