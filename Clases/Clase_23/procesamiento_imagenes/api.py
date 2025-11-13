from flask import Flask, request, jsonify
from tasks import procesar_imagen
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    """Endpoint para subir imagen"""
    file = request.files['image']
    operaciones = request.form.getlist('operaciones')
    
    # Guardar archivo
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    
    # Enviar a Celery
    task = procesar_imagen.delay(filepath, operaciones)
    
    return jsonify({
        'task_id': task.id,
        'status': 'processing'
    })

@app.route('/status/<task_id>')
def task_status(task_id):
    """Verificar estado de tarea"""
    task = procesar_imagen.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Esperando...'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)