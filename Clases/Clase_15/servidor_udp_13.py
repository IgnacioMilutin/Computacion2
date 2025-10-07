import socket

HOST, PORT = "0.0.0.0", 9013

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST, PORT))
    print(f"UDP eco en {HOST}:{PORT}")
    while True:
        data, addr = s.recvfrom(4096)
        print(f"{addr} -> {data!r}")
        s.sendto(data, addr)