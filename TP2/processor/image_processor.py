"""
Procesamiento de imágenes y generación de thumbnails.
"""

import time
import io
import base64
import requests
from PIL import Image
from typing import List, Dict, Tuple
from common.errors import ProcessingError
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_and_process_images(url: str, max_images: int = 5):
        """
        Extrae imágenes de la URL y las procesa.
        Esta función se ejecuta en un proceso separado.
        
        Args:
            url: URL a procesar
            max_images: Número máximo de imágenes a procesar
        
        Returns:
            Lista de thumbnails procesados
        """
        
        max_size_html = 5 * 1024 * 1024
        retries=3
        delay=1

        for attempt in range(retries):
            try:
                # Fetch HTML
                response = requests.get(
                    url, 
                    timeout=30, 
                    headers={'User-Agent': 'Mozilla/5.0 Web Scraper Bot'}
                )
                response.raise_for_status()

                if len(response.content) > max_size_html:
                    raise ProcessingError(
                        f"La página {url} excede el tamaño máximo permitido de {max_size_html / (1024*1024)} MB"
                )

                html = BeautifulSoup(response.text, 'lxml')
                
                # Extraer URLs de imágenes
                image_urls = []
                for img in html.find_all('img', src=True)[:max_images * 2]:
                    src = urljoin(url, img['src'])
                    image_urls.append(src)
                
                # Procesar imágenes
                return process_images(image_urls[:max_images], max_images)
            
            except requests.RequestException as e:
                if attempt < retries - 1:
                    print(f"[WARN] Error descargando HTML desde {url} (intento {attempt+1}/{retries}), reintentando...")
                    time.sleep(delay)
                    continue
                else:
                    raise ProcessingError(f"Error al descargar HTML desde {url}, no se logro acceder al dominio tras {retries} intentos. Error:: {e}")
            
            except ProcessingError:
                raise

            except Exception as e:
                raise ProcessingError(f"Error inesperado al procesar imágenes de {url}: {e}")


def process_images(image_urls: List[str], max_images: int = 5) -> List[Dict[str, str]]:
    """
    Descarga y procesa imágenes generando thumbnails.
    
    Args:
        image_urls: Lista de URLs de imágenes
        max_images: Número máximo de imágenes a procesar
    
    Returns:
        Lista de dicts con thumbnails en base64
    
    Raises:
        ProcessingError: Si hay errores al procesar
    """
    results = []
    
    for url in image_urls[:max_images]:
        try:
            thumbnail = generate_thumbnail(url)
            if thumbnail:
                results.append({
                    'original_url': url,
                    'thumbnail_base64': thumbnail,
                    'status': 'success'
                })
        except Exception as e:
            results.append({
                'original_url': url,
                'thumbnail_base64': None,
                'status': 'error',
                'error': str(e)
            })
    
    return results


def generate_thumbnail(
    image_url: str,
    size: Tuple[int, int] = (200, 200),
    quality: int = 85
) -> str:
    """
    Genera un thumbnail optimizado de una imagen.
    
    Args:
        image_url: URL de la imagen
        size: Tupla (ancho, alto) del thumbnail
        quality: Calidad JPEG (1-100)
    
    Returns:
        Thumbnail en base64
    
    Raises:
        ProcessingError: Si hay errores al generar thumbnail
    """
    try:
        # Descargar imagen
        response = requests.get(
            image_url,
            timeout=10,
            headers={'User-Agent': 'Mozilla/5.0 Web Scraper Bot'}
        )
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '').lower()

        # No es una imagen
        if not content_type.startswith('image/'):
            raise ProcessingError(
                f"La URL no devuelve una imagen válida (Content-Type: {content_type})"
            )

        # Es SVG (no soportado por Pillow)
        if 'svg' in content_type:
            raise ProcessingError(
                f"Formato SVG no soportado para la imagen: {image_url}"
            )
        
        # Abrir con PIL
        image = Image.open(io.BytesIO(response.content))
        
        # Convertir RGBA a RGB si es necesario
        if image.mode == 'RGBA':
            # Crear fondo blanco
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])  # Alpha channel como mask
            image = background
        elif image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # Generar thumbnail (mantiene aspect ratio)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Convertir a bytes
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        
        # Codificar en base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    except requests.RequestException as e:
        raise ProcessingError(f"Error al descargar imagen {image_url}: {e}")
    except Exception as e:
        raise ProcessingError(f"Error al procesar imagen {image_url}: {e}")