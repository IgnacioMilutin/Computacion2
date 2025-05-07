from multiprocessing import Process
import time

def worker():
    print("Proceso iniciado")
    time.sleep(2)
    print("Proceso finalizado")

if __name__ == "__main__":
    p = Process(target=worker)
    p.start()
    p.join()  # Espera a que el proceso termine
    print("Proceso principal ha terminado")
