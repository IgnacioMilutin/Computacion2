import json
import base64
from typing import Any, Dict
from datetime import datetime

# serializador a JSON
def serialize_data(data: Dict[str, Any]) -> str:
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        raise TypeError(f"Tipo {type(obj)} no serializable")
    
    return json.dumps(data, default=default_serializer, ensure_ascii=False)


# deserializador de JSON a diccionario
def deserialize_data(json_str: str) -> Dict[str, Any]:
    return json.loads(json_str)