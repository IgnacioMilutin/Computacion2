import socket

HOST, PORT = "127.0.0.1", 9012
IDLE_TIMEOUT = 10  # segundos

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(8)
    print(f"Timeout server en {HOST}:{PORT} (IDLE={IDLE_TIMEOUT}s)")

    while True:
        conn, addr = srv.accept()
        with conn:
            conn.settimeout(IDLE_TIMEOUT)
            try:
                while True:
                    b = conn.recv(4096)
                    if not b:
                        break
                    conn.sendall(b)
            except socket.timeout:
                print("Inactividad excedida para", addr)
                # cierre implícito al salir del with