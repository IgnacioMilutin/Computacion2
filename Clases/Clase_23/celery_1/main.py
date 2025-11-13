from tasks import sumar, tarea_larga

# Ejecutar tarea de forma asíncrona
result = sumar.delay(4, 6)

# Continuar sin esperar
print("Tarea enviada, continuando...")

# Obtener resultado (esto bloquea hasta que termine)
print(f"Resultado: {result.get(timeout=10)}")