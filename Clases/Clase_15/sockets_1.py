import socket
import os

SOCKET_PATH = "/tmp/eco.sock"

def main():
    if not os.path.exists(SOCKET_PATH):
        raise SystemExit(f"No existe {SOCKET_PATH}. ¿Arrancaste `nc -lU {SOCKET_PATH}`?")

    # AF_UNIX = dominio local (archivo-socket), STREAM = estilo TCP
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.connect(SOCKET_PATH)
        s.sendall(b"hola desde UDS\n")
        # `nc` no hace eco automático, pero podés teclear algo y ENTER en la terminal del nc
        # para que el cliente lo lea. Si no hay datos, recv puede bloquear.
        data = s.recv(4096)
        print(f"< {data!r}")

if __name__ == "__main__":
    main()