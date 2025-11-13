from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urljoin, urlparse


# Parsea HTML y extrae información
def parse_html(html_content: str, base_url: str = '') -> Dict:
    html = BeautifulSoup(html_content, 'lxml')
    
    return {
        'title': _extract_title(html),
        'links': _extract_links(html, base_url),
        'structure': _extract_structure(html),
        'images_count': len(html.find_all('img')),
    }


# Extrae el título de la página
def _extract_title(html: BeautifulSoup) -> str:
    if html.title and html.title.string:
        return html.title.string.strip()
    
    h1 = html.find('h1')
    if h1:
        return h1.get_text(strip=True)
    
    return "Sin título"


# Extrae los links de la pagina
def _extract_links(html: BeautifulSoup, base_url: str) -> List[str]:

    links = []
    seen = set()
    
    for a_tag in html.find_all('a', href=True):
        href = a_tag['href'].strip()
        
        if not href or href.startswith('#') or href.startswith('javascript:'):
            continue
        
        if base_url:
            absolute_url = urljoin(base_url, href)
        else:
            absolute_url = href
        
        if absolute_url not in seen:
            seen.add(absolute_url)
            links.append(absolute_url)
    
    return links


# Extrae la estructura de headers de la página
def _extract_structure(html: BeautifulSoup) -> Dict[str, int]:
    return {
        'h1': len(html.find_all('h1')),
        'h2': len(html.find_all('h2')),
        'h3': len(html.find_all('h3')),
        'h4': len(html.find_all('h4')),
        'h5': len(html.find_all('h5')),
        'h6': len(html.find_all('h6'))
    }
