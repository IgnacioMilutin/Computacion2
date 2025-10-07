import socket
import socketserver
import threading
import time

estadisticas={'conexiones IPv4':0,'conexiones IPv6':0,'tiempo_de_respuesta':0,'bytes_transferidos': 0}

class ManejadorUniversal(socketserver.BaseRequestHandler):
    def handle(self):
        # Detectar tipo de conexión a traves de los ':'
        if self.client_address[0].count(':') > 1:
            protocolo = "IPv6"
        else:
            protocolo = "IPv4"
        
        print(f"[{protocolo}] Conexión de: {self.client_address}")
                

        data = self.request.recv(1024).strip()
        inicio = time.time()
        respuesta = f"Servidor {protocolo}: {data.decode()}"
        self.request.sendall(respuesta.encode())
        fin = time.time()
        duracion = fin - inicio
        bytes_transferidos=len(data)+len(respuesta.encode())

        if protocolo=='IPv4':
            estadisticas["conexiones IPv4"] += 1
        else: estadisticas["conexiones IPv6"] += 1
        estadisticas["tiempo_de_respuesta"] += duracion
        estadisticas["bytes_transferidos"] += bytes_transferidos

class ServidorIPv4(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET

class ServidorIPv6(socketserver.ThreadingTCPServer):
    address_family = socket.AF_INET6

def iniciar_servidor(familia, host, port, handler):
    """Inicia un servidor en un hilo separado"""
    if familia == socket.AF_INET:
        servidor = ServidorIPv4((host, port), handler)
        nombre = "IPv4"
    else:
        servidor = ServidorIPv6((host, port), handler)
        nombre = "IPv6"
    
    print(f"Iniciando servidor {nombre} en {host}:{port}")
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    return servidor, thread

def reporte(estadisticas):
    if (estadisticas['conexiones IPv4']+estadisticas['conexiones IPv6'])==0:
        tiempo_promedio=0
    else: tiempo_promedio=estadisticas["tiempo_de_respuesta"]/(estadisticas['conexiones IPv4']+estadisticas['conexiones IPv6'])
    print(f"conexiones IPv4: {estadisticas['conexiones IPv4']}")
    print(f"conexiones IPv6: {estadisticas['conexiones IPv6']}")
    print(f"tiempo promedio de respuesta: {tiempo_promedio}")
    print(f"bytes_totales_transferidos: {estadisticas['bytes_transferidos']}")

if __name__ == "__main__":
    PORT = 9999
    servidores = []
    
    # Obtener direcciones disponibles
    direcciones = socket.getaddrinfo(
        "localhost", 
        PORT, 
        socket.AF_UNSPEC, 
        socket.SOCK_STREAM
    )
    
    # Iniciar servidor para cada familia de direcciones
    familias_iniciadas = set()
    for addr_info in direcciones:
        familia = addr_info[0]
        if familia not in familias_iniciadas:
            host = "127.0.0.1" if familia == socket.AF_INET else "::1"
            srv, thread = iniciar_servidor(
                familia, host, PORT, ManejadorUniversal
            )
            servidores.append(srv)
            familias_iniciadas.add(familia)
    
    print("\nServidores iniciados. Presiona Ctrl+C para detener.")
    
    try:
        for srv in servidores:
            srv.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for srv in servidores:
            srv.shutdown()
        reporte(estadisticas)   