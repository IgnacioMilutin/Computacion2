from multiprocessing import Process, Pipe

def hijo(conn):
    conn.send("Hola desde el hijo")
    conn.close()

if __name__ == "__main__":
    padre_conn, hijo_conn = Pipe()
    p = Process(target=hijo, args=(hijo_conn,))
    p.start()
    print(padre_conn.recv())  # Espera el mensaje del hijo
    p.join()
