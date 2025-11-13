"""
Parser de HTML para extracción de información estructurada.
"""

from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urljoin, urlparse


def parse_html(html_content: str, base_url: str = '') -> Dict:
    """
    Parsea HTML y extrae información estructurada.
    
    Args:
        html_content: Contenido HTML
        base_url: URL base para resolver enlaces relativos
    
    Returns:
        Dict con título, enlaces, estructura, imágenes, etc.
    """
    html = BeautifulSoup(html_content, 'lxml')
    
    return {
        'title': _extract_title(html),
        'links': _extract_links(html, base_url),
        'structure': _extract_structure(html),
        'images_count': len(html.find_all('img')),
    }


def _extract_title(html: BeautifulSoup) -> str:
    """Extrae el título de la página"""
    if html.title and html.title.string:
        return html.title.string.strip()
    
    # Intentar con h1 si no hay title
    h1 = html.find('h1')
    if h1:
        return h1.get_text(strip=True)
    
    return "Sin título"


def _extract_links(html: BeautifulSoup, base_url: str) -> List[str]:
    """
    Extrae todos los enlaces de la página.
    
    Args:
        html: Objeto BeautifulSoup
        base_url: URL base para resolver enlaces relativos
    
    Returns:
        Lista de URLs absolutas únicas
    """
    links = []
    seen = set()
    
    for a_tag in html.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        # Ignorar enlaces vacíos o anclas
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
        
        # Resolver URL relativa
        if base_url:
            absolute_url = urljoin(base_url, href)
        else:
            absolute_url = href
        
        # Añadir solo si no lo hemos visto
        if absolute_url not in seen:
            seen.add(absolute_url)
            links.append(absolute_url)
    
    return links


def _extract_structure(html: BeautifulSoup) -> Dict[str, int]:
    """
    Extrae la estructura de headers de la página.
    
    Returns:
        Dict con conteo de cada tipo de header (h1-h6)
    """
    return {
        'h1': len(html.find_all('h1')),
        'h2': len(html.find_all('h2')),
        'h3': len(html.find_all('h3')),
        'h4': len(html.find_all('h4')),
        'h5': len(html.find_all('h5')),
        'h6': len(html.find_all('h6'))
    }
