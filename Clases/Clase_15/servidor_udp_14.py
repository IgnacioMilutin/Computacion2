import socket
import time

HOST, PORT = "0.0.0.0", 9014

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"UDP TIME en {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(2048)
        msg = data.decode("utf-8", "replace").strip()
        if msg == "TIME":
            s.sendto(time.strftime("%H:%M:%S").encode(), addr)
        else:
            s.sendto(b"ERR\n", addr)