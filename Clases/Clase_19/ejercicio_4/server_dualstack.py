import socket
import socketserver
import threading

class ManejadorUniversal(socketserver.BaseRequestHandler):
    def handle(self):
        # Detectar tipo de conexión a traves de los ':'
        if self.client_address[0].count(':') > 1:
            protocolo = "IPv6"
        else:
            protocolo = "IPv4"
        
        print(f"[{protocolo}] Conexión de: {self.client_address}")
        
        data = self.request.recv(1024).strip()
        respuesta = f"Servidor {protocolo}: {data.decode()}"
        self.request.sendall(respuesta.encode())

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