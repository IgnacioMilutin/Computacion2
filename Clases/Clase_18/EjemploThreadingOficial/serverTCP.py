import socket
import threading
import socketserver

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = f"{cur_thread.name}:{data}"
        self.request.sendall(response.encode("ascii"))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address=True

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address
        #server_thread = threading.Thread(target=server.serve_forever)
        #server_thread.daemon = True
        #server_thread.start()
        #server_thread.join()
        server.serve_forever()