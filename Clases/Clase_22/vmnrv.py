from concurrent.futures import ThreadPoolExecutor
import time

def tarea_lenta(n):
    time.sleep(2)
    return n * 2

executor = ThreadPoolExecutor(max_workers=2)

# submit() retorna un Future inmediatamente
future = executor.submit(tarea_lenta, 10)

print(f"Future creado: {future}")
print(f"¿Está corriendo? {future.running()}")
print(f"¿Terminó? {future.done()}")

# result() bloquea hasta que termine
resultado = future.result()  # Espera ~2s aquí
print(f"Resultado: {resultado}")

executor.shutdown()