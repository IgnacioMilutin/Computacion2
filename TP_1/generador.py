import time
import random
from datetime import datetime
from multiprocessing import Pipe

def generador():
    data={
            "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "frecuencia":random.randint(60,180),
            "presion":[random.randint(110,180),random.randint(70,110)],
            "oxigeno":random.randint(90,100)
        }
    return data

def proceso_generador(tipos,pipes):
    for i in range(60):
        data=generador()
        for pipe in pipes:
            pipe.send(data)
        time.sleep(1)
    
    for pipe in pipes:
        pipe.send('fin')
    
    for pipe in pipes:
        pipe.close()