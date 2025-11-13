from celery_app import app
import time

@app.task
def sumar(x, y):
    """Tarea simple"""
    time.sleep(2)  # Simular trabajo
    return x + y

@app.task
def tarea_larga():
    """Tarea que tarda mucho"""
    time.sleep(60)
    return "Terminé después de 1 minuto"