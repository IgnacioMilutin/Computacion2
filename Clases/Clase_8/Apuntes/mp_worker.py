import time

def tarea_lenta(nombre):
    print(f"Inicio tarea {nombre}")
    time.sleep(2)  # Simula tarea lenta
    print(f"Fin tarea {nombre}")

if __name__ == "__main__":
    inicio = time.time()
    for i in range(4):
        tarea_lenta(f"tarea-{i}")
    fin = time.time()
    print(f"Tiempo total: {fin - inicio:.2f} segundos")
