from multiprocessing import Process, Lock, Value

def sumar(contador, lock):
    for _ in range(100000):
        with lock:
            contador.value += 1

if __name__ == "__main__":
    contador = Value('i', 0)
    lock = Lock()
    p1 = Process(target=sumar, args=(contador, lock))
    p2 = Process(target=sumar, args=(contador, lock))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Valor final:", contador.value)  # Ahora es correcto
