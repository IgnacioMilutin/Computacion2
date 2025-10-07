import socket

HOST, PORT = "127.0.0.1", 9010

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)  # backlog
    print(f"Escuchando en {HOST}:{PORT} ... Ctrl+C para salir")

    while True:  # loop de sesiones (secuenciales)
        conn, addr = srv.accept()
        print("Conexión de", addr)
        with conn:
            while True:
                b = conn.recv(4096)
                if not b:
                    break  # peer cerró
                conn.sendall(b)  # eco
        print("Cierre de", addr)