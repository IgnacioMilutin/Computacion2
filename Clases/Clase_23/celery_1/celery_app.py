from celery import Celery

# Crear instancia de Celery
app = Celery(
    'mi_proyecto',
    broker='redis://localhost:6379/0',      # Dónde está el broker
    backend='redis://localhost:6379/1',     # Dónde guardar resultados
)

# Configuración básica
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Mendoza',
    enable_utc=True,
)

# Autodescubrir tareas en módulos
app.autodiscover_tasks(['mi_proyecto'])