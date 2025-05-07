from multiprocessing import Process, current_process
import time

def tarea():
    print(f"Inicio: {current_process().name}, PID={current_process().pid}")
    time.sleep(1)
    print(f"Fin: {current_process().name}")

if __name__ == "__main__":
    procesos = []
    for i in range(3):
        p = Process(target=tarea, name=f"Proceso-{i}")
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    print("Todos los procesos han terminado.")
