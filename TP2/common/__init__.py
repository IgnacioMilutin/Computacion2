"""
Módulo común para comunicación y utilidades compartidas
entre el servidor de scraping y el servidor de procesamiento.
"""

from .protocol import send_message, receive_message
from .serialization import serialize_data, deserialize_data
from .errors import (
    ScrapingError,
    ProcessingError
)