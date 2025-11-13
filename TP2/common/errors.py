"""
Excepciones personalizadas para el sistema de scraping distribuido.
"""


class ScrapingError(Exception):
    """Error base para problemas de scraping"""
    pass


class ProcessingError(Exception):
    """Error base para problemas de procesamiento"""
    pass


class NetworkError(Exception):
    """Error de comunicación de red"""
    pass


class TimeoutError(Exception):
    """Error de timeout en operaciones"""
    pass


class InvalidURLError(ScrapingError):
    """URL inválida o inaccesible"""
    pass


class RateLimitError(ScrapingError):
    """Se excedió el límite de rate limiting"""
    pass


class CacheError(Exception):
    """Error relacionado con el caché"""
    pass