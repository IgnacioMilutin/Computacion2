"""
Utilidades de serialización y deserialización de datos.
"""

import json
import base64
from typing import Any, Dict
from datetime import datetime


def serialize_data(data: Dict[str, Any]) -> str:
    """
    Serializa datos a JSON, manejando tipos especiales.
    
    Args:
        data: Diccionario a serializar
    
    Returns:
        String JSON
    """
    def default_serializer(obj):
        """Maneja tipos no serializables por defecto"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        raise TypeError(f"Tipo {type(obj)} no serializable")
    
    return json.dumps(data, default=default_serializer, ensure_ascii=False)


def deserialize_data(json_str: str) -> Dict[str, Any]:
    """
    Deserializa JSON a diccionario.
    
    Args:
        json_str: String JSON
    
    Returns:
        Diccionario con los datos
    """
    return json.loads(json_str)


def encode_image_base64(image_bytes: bytes) -> str:
    """
    Codifica imagen en base64 para transmisión.
    
    Args:
        image_bytes: Bytes de la imagen
    
    Returns:
        String base64
    """
    return base64.b64encode(image_bytes).decode('utf-8')


def decode_image_base64(base64_str: str) -> bytes:
    """
    Decodifica imagen desde base64.
    
    Args:
        base64_str: String base64
    
    Returns:
        Bytes de la imagen
    """
    return base64.b64decode(base64_str)