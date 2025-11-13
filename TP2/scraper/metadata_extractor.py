from bs4 import BeautifulSoup
from typing import Dict, Optional


# Extrae metadatos de la pagina
def extract_metadata(html_content: str) -> Dict[str, any]:
    html = BeautifulSoup(html_content, "lxml")

    meta_tags = {}
    meta_tags.update(_extract_basic_meta(html))
    meta_tags.update(_extract_open_graph(html))

    return meta_tags


# Extrae metadatos descripciones y keywords de la pagina
def _extract_basic_meta(html: BeautifulSoup) -> Dict[str, str]:
    meta_info = {}
    for name in ["description", "keywords"]:
        tag = html.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            meta_info[name] = tag["content"].strip()
    return meta_info


# Extrae metadatos Open Graph de la pagina
def _extract_open_graph(html: BeautifulSoup) -> Dict[str, str]:
    og_info = {}
    for tag in html.find_all("meta", attrs={"property": lambda x: x and x.startswith("og:")}):
        prop = tag.get("property")
        content = tag.get("content")
        if prop and content:
            og_info[prop] = content.strip()
    return og_info