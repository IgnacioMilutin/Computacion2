from multiprocessing import Process
import time

def tarea_lenta(nombre):
    print(f"Inicio tarea {nombre}")
    time.sleep(2)
    print(f"Fin tarea {nombre}")

if __name__ == "__main__":
    procesos = []
    inicio = time.time()

    for i in range(4):
        p = Process(target=tarea_lenta, args=(f"tarea-{i}",))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    fin = time.time()
    print(f"Tiempo total: {fin - inicio:.2f} segundos")
