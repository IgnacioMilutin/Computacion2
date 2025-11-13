from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageFilter
import time
from pathlib import Path

def procesar_imagen(ruta_entrada):
    """Aplica blur a una imagen"""
    try:
        # Abrir imagen
        img = Image.open(ruta_entrada)
        
        # Aplicar filtro (operación CPU-bound)
        img_procesada = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # Guardar resultado
        ruta_salida = Path("procesadas") / ruta_entrada.name
        img_procesada.save(ruta_salida)
        
        return f"✓ {ruta_entrada.name}"
    
    except Exception as e:
        return f"✗ {ruta_entrada.name}: {e}"

def procesar_secuencial(imagenes):
    """Versión secuencial para comparación"""
    inicio = time.time()
    
    for imagen in imagenes:
        procesar_imagen(imagen)
    
    return time.time() - inicio

def procesar_paralelo(imagenes, num_workers=None):
    """Versión paralela con ProcessPoolExecutor"""
    inicio = time.time()
    
    # None usa cpu_count()
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # map() mantiene el orden
        resultados = executor.map(procesar_imagen, imagenes)
        
        # Consumir el iterador
        for resultado in resultados:
            print(resultado)
    
    return time.time() - inicio

# Uso
if __name__ == "__main__":
    Path("procesadas").mkdir(exist_ok=True)
    imagenes = list(Path("imagenes").glob("*.jpg"))
    
    print(f"Procesando {len(imagenes)} imágenes...\n")
    
    # Comparación
    tiempo_seq = procesar_secuencial(imagenes[:3])  # Solo 10 para test
    print(f"\nSecuencial: {tiempo_seq:.2f}s")
    
    tiempo_par = procesar_paralelo(imagenes[:10], num_workers=4)
    print(f"Paralelo (4 cores): {tiempo_par:.2f}s")
    print(f"Speedup: {tiempo_seq/tiempo_par:.2f}x")