"""
Extractor de metadatos de páginas web.
"""

from bs4 import BeautifulSoup
from typing import Dict, Optional


def extract_metadata(html_content: str) -> Dict[str, any]:
    """
    Extrae todos los metadatos relevantes de una página.
    
    Args:
        html_content: Contenido HTML
    
    Returns:
        Dict con metadatos estructurados
    """
    html = BeautifulSoup(html_content, "lxml")

    # Llamar a las funciones auxiliares
    meta_tags = {}
    meta_tags.update(_extract_basic_meta(html))
    meta_tags.update(_extract_open_graph(html))

    return meta_tags


def _extract_basic_meta(html: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags básicos como description y keywords.

    Args:
        html: Objeto BeautifulSoup

    Returns:
        Diccionario con meta tags básicos
    """
    meta_info = {}
    for name in ["description", "keywords"]:
        tag = html.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            meta_info[name] = tag["content"].strip()
    return meta_info


def _extract_open_graph(html: BeautifulSoup) -> Dict[str, str]:
    """
    Extrae meta tags del tipo Open Graph (og:*)

    Args:
        html: Objeto BeautifulSoup

    Returns:
        Diccionario con tags Open Graph
    """
    og_info = {}
    for tag in html.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")}):
        prop = tag.get("property")
        content = tag.get("content")
        if prop and content:
            og_info[prop] = content.strip()
    return og_info