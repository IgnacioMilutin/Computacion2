from multiprocessing import Process, Queue

def hijo(q):
    q.put("Mensaje desde el proceso hijo")

if __name__ == "__main__":
    q = Queue()
    p = Process(target=hijo, args=(q,))
    p.start()
    print(q.get())  # Recibe el mensaje
    p.join()
