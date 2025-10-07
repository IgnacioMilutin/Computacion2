from multiprocessing import Process, Pipe
import numpy as np
import json

def proceso_analizador(tipo,pipe,queue,semaforo):
    valores=[]
    valores_presion_1=[]
    valores_presion_2=[]
    ventana=30

    while True:
        try:
            data=pipe.recv()
            if data=='fin':
                break
        except EOFError:
            break

        timestamp=data['timestamp']

        if tipo=='presion':
            valor_presion_1=data['presion'][0]
            valor_presion_2=data['presion'][1]
            valores_presion_1.append(valor_presion_1)
            valores_presion_2.append(valor_presion_2)
        elif tipo=='frecuencia' or tipo=='oxigeno':
            valor=data[tipo] 
            valores.append(valor)
        else: return 'tipo de dato no reconocido'

        if len(valores) > ventana:
            valores.pop(0)

        if len(valores_presion_1) > ventana:
            valores_presion_1.pop(0)
        
        if len(valores_presion_2) > ventana:
            valores_presion_2.pop(0)

        if tipo=='presion':
            media_1=round(np.mean(valores_presion_1),2)
            media_2=round(np.mean(valores_presion_2),2)
            media=[float(media_1),float(media_2)]
            desviacion_1=round(np.std(valores_presion_1),2)
            desviacion_2=round(np.std(valores_presion_2),2)
            desviacion=[float(desviacion_1),float(desviacion_2)]
        elif tipo=='frecuencia' or tipo=='oxigeno':
            media=float(round(np.mean(valores),2))
            desviacion=float(round(np.std(valores),2))
        else: return 'tipo de dato no reconocido'

        resultado= {
            'tipo':tipo,
            'timestamp':timestamp,
            'valor':data[tipo],
            'media': media,
            'desv': desviacion   
        }

        queue.put(resultado)
        semaforo.acquire()
      
    queue.put({'tipo':'fin'})
    pipe.close()