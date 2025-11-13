"""
Protocolo de comunicación TCP entre servidores.
Formato: [4 bytes longitud (big-endian)][payload JSON]
"""

import struct
import json
import asyncio
from typing import Dict, Any
from .errors import NetworkError
from time import time


def send_message(sock, data: Dict[str, Any], retries: int = 3, delay: int = 1) -> None:
    """
    Envía un mensaje a través de un socket con protocolo de longitud.
    
    Args:
        sock: Socket para enviar datos
        data: Diccionario a enviar (será serializado a JSON)
    
    Raises:
        NetworkError: Si hay problemas al enviar
    """
    message = json.dumps(data).encode('utf-8')
    length = struct.pack('!I', len(message))

    for attempt in range(retries):
        try:
            sock.sendall(length + message)
            return
        except (BrokenPipeError, ConnectionResetError, TimeoutError) as e:
            if attempt < retries-1:
                print(f"[WARN] Error enviando mensaje ({attempt+1}/{retries}), reintentando...")
                time.sleep(delay)
                continue
            raise NetworkError(f"Error al enviar mensaje tras {retries+1} intentos: {e}")
        except Exception as e:
            raise NetworkError(f"Error inesperado al enviar mensaje: {e}")


def receive_message(sock, retries: int = 3, delay: int = 1) -> Dict[str, Any]:
    """
    Recibe un mensaje de un socket con protocolo de longitud.
    
    Args:
        sock: Socket para recibir datos
    
    Returns:
        Diccionario con los datos recibidos
    
    Raises:
        NetworkError: Si hay problemas al recibir
    """
    for attempt in range(retries):
        try:
            # Leer longitud del mensaje (4 bytes)
            length_bytes = sock.recv(4)
            if not length_bytes or len(length_bytes) < 4:
                raise NetworkError("Conexión cerrada o datos incompletos")
            
            length = struct.unpack('!I', length_bytes)[0]
            
            # Leer el mensaje completo
            data = b''
            while len(data) < length:
                chunk = sock.recv(min(length - len(data), 4096))
                if not chunk:
                    raise NetworkError("Conexión cerrada antes de recibir mensaje completo")
                data += chunk
            
            return json.loads(data.decode('utf-8'))
        
        except (TimeoutError, ConnectionResetError) as e:
            if attempt < retries-1:
                print(f"[WARN] Error recibiendo mensaje ({attempt+1}/{retries}), reintentando...")
                time.sleep(delay)
                continue
            raise NetworkError(f"Error al recibir mensaje tras {retries+1} intentos: {e}")

        except json.JSONDecodeError as e:
            raise NetworkError(f"Error al decodificar JSON: {e}")

        except Exception as e:
            raise NetworkError(f"Error inesperado al recibir mensaje: {e}")


async def async_send_message(writer: asyncio.StreamWriter, data: Dict[str, Any], retries: int = 3, delay: int = 1) -> None:
    """
    Versión asíncrona de send_message para asyncio.
    
    Args:
        writer: StreamWriter de asyncio
        data: Diccionario a enviar
    """
    message = json.dumps(data).encode('utf-8')
    length = struct.pack('!I', len(message))

    for attempt in range(retries):
        try:
            writer.write(length + message)
            await writer.drain()
            return
        except (ConnectionResetError, TimeoutError, BrokenPipeError) as e:
            if attempt < retries-1:
                print(f"[WARN] Error enviando mensaje async ({attempt+1}/{retries}), reintentando...")
                await asyncio.sleep(delay)
                continue
            raise NetworkError(f"Error al enviar mensaje async tras {retries+1} intentos: {e}")
        except Exception as e:
            raise NetworkError(f"Error inesperado al enviar mensaje async: {e}")


async def async_receive_message(reader: asyncio.StreamReader, retries: int = 3, delay: int = 1) -> Dict[str, Any]:
    """
    Versión asíncrona de receive_message para asyncio.
    
    Args:
        reader: StreamReader de asyncio
    
    Returns:
        Diccionario con los datos recibidos
    """
    for attempt in range(retries):
        try:
            # Leer longitud
            length_bytes = await reader.readexactly(4)
            length = struct.unpack('!I', length_bytes)[0]
            
            # Leer mensaje
            data = await reader.readexactly(length)
            return json.loads(data.decode('utf-8'))
        
        except (asyncio.IncompleteReadError, ConnectionResetError) as e:
            if attempt < retries-1:
                print(f"[WARN] Error recibiendo mensaje async ({attempt+1}/{retries}), reintentando...")
                await asyncio.sleep(delay)
                continue
            raise NetworkError(f"Error al recibir mensaje async tras {retries+1} intentos: {e}")

        except json.JSONDecodeError as e:
            raise NetworkError(f"Error al decodificar JSON: {e}")

        except Exception as e:
            raise NetworkError(f"Error inesperado al recibir mensaje async: {e}")