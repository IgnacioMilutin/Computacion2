from multiprocessing import Pool
import time

def tarea_lenta(x):
    time.sleep(1)
    return x * 2

if __name__ == "__main__":
    with Pool(processes=2) as pool:
        result1 = pool.apply_async(tarea_lenta, args=(5,))
        result2 = pool.apply_async(tarea_lenta, args=(10,))
        print(result1.get())  # Espera y devuelve el resultado
        print(result2.get())
