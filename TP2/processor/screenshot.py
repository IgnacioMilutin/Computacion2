import base64
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from common.errors import ProcessingError


# Genera un screenshot de la página web
def generate_screenshot(
    url: str,
    full_page: bool = True,
    width: int = 1280,
    height: int = 720,
    timeout: int = 30000,
    max_size_mb: int = 5
) -> str:
    
    retries = 3
    delay = 1

    for attempt in range(retries):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                context = browser.new_context(
                    viewport={'width': width, 'height': height},
                    user_agent='Mozilla/5.0 Web Scraper Bot'
                )
                
                page = context.new_page()
                
                try:
                    page.goto(url, timeout=timeout, wait_until='networkidle')
                except PlaywrightTimeout:
                    page.goto(url, timeout=timeout, wait_until='domcontentloaded')
                
                screenshot_bytes = page.screenshot(
                    full_page=full_page,
                    type='png'
                )

                screenshot_size_mb = len(screenshot_bytes) / (1024 * 1024)
                if screenshot_size_mb > max_size_mb:
                    if full_page:
                        screenshot_bytes = page.screenshot(full_page=False, type='png')
                        screenshot_size_mb = len(screenshot_bytes) / (1024 * 1024)
                        if screenshot_size_mb > max_size_mb:
                            raise ProcessingError(
                                f"El screenshot reducido de {url} excede el límite de {max_size_mb} MB "
                                f"({screenshot_size_mb:.2f} MB)"
                            )
                    else:
                        raise ProcessingError(
                            f"El screenshot de {url} excede el límite de {max_size_mb} MB "
                            f"({screenshot_size_mb:.2f} MB reales)"
                        )
                
                context.close()
                browser.close()
                
                return base64.b64encode(screenshot_bytes).decode('utf-8')
        
        except Exception as e:
            if attempt < retries - 1:
                print(f"[WARN] Error generando screenshot de {url} (intento {attempt+1}/{retries}), reintentando...")
                time.sleep(delay)
            else:
                raise ProcessingError(f"Error al generar screenshot de {url} tras {retries} intentos. ERROR: {e}")