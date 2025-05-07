from multiprocessing import Process, Value
import time

def incrementar(contador):
    for _ in range(100):
        time.sleep(0.01)
        with contador.get_lock():  # 🔐 importante
            contador.value += 1

if __name__ == "__main__":
    contador = Value('i', 0)
    p1 = Process(target=incrementar, args=(contador,))
    p2 = Process(target=incrementar, args=(contador,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"Contador final: {contador.value}")  # Esperamos 200
