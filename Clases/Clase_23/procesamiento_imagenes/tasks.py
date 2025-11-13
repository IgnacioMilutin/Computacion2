from celery_app import app
from PIL import Image, ImageFilter, ImageEnhance
import time
import os

@app.task(bind=True)  # bind=True para acceder a self
def procesar_imagen(self, ruta_imagen, operaciones):
    """
    Procesa una imagen con múltiples operaciones.
    
    Args:
        ruta_imagen: Path a la imagen
        operaciones: Lista de operaciones ['blur', 'rotate', 'resize']
    """
    try:
        # Actualizar estado
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': len(operaciones), 'status': 'Iniciando...'}
        )
        
        img = Image.open(ruta_imagen)
        
        for i, operacion in enumerate(operaciones):
            # Actualizar progreso
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': len(operaciones),
                    'status': f'Aplicando {operacion}...'
                }
            )
            
            if operacion == 'blur':
                img = img.filter(ImageFilter.GaussianBlur(radius=5))
            elif operacion == 'rotate':
                img = img.rotate(90)
            elif operacion == 'resize':
                img = img.resize((800, 600))
            elif operacion == 'enhance':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
            
            time.sleep(1)  # Simular procesamiento pesado
        
        # Guardar resultado
        output_path = ruta_imagen.replace('.jpg', '_procesada.jpg')
        img.save(output_path)
        
        return {
            'status': 'success',
            'output_path': output_path,
            'operaciones_aplicadas': operaciones
        }
    
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise

@app.task
def limpiar_archivos_temporales(edad_dias=7):
    """Tarea de limpieza periódica"""
    import datetime
    
    ahora = datetime.datetime.now()
    archivos_eliminados = 0
    
    for archivo in os.listdir('uploads'):
        ruta = os.path.join('uploads', archivo)
        if os.path.isfile(ruta):
            fecha_creacion = datetime.datetime.fromtimestamp(
                os.path.getctime(ruta)
            )
            
            if (ahora - fecha_creacion).days > edad_dias:
                os.remove(ruta)
                archivos_eliminados += 1
    
    return f"Eliminados {archivos_eliminados} archivos"