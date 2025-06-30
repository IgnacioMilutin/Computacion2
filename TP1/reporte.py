import json
import numpy as np

def generador_reporte():
    archivo_blockchain='blockchain.json'
    archivo_reporte='reporte.txt'
    with open(archivo_blockchain,'r') as archivo:
        blockchain=json.load(archivo)

    total_bloques=len(blockchain)
    frecuencias=[]
    oxigenos=[]
    presiones_1=[]
    presiones_2=[]
    alertas=[]

    for i,bloque in enumerate(blockchain):
        frecuencia=bloque['datos']['frecuencia']['valor']
        oxigeno=bloque['datos']['oxigeno']['valor']
        presion_1=bloque['datos']['presion']['valor'][0]
        presion_2=bloque['datos']['presion']['valor'][1]

        frecuencias.append(frecuencia)
        oxigenos.append(oxigeno)
        presiones_1.append(presion_1)
        presiones_2.append(presion_2)

        if bloque.get('alerta')==True:
            alertas.append([i,bloque['timestamp']])

    promedio_frecuencia=round(np.mean(frecuencias),2)
    promedio_oxigeno=round(np.mean(oxigenos),2)
    promedio_presion_1=round(np.mean(presiones_1),2)
    promedio_presion_2=round(np.mean(presiones_2),2)

    with open(archivo_reporte, 'w') as f:
        f.write("=== REPORTE DE LA BLOCKCHAIN BIOMÉTRICA ===\n")
        f.write(f"Total de bloques: {total_bloques}\n")
        f.write(f"Bloques con alerta: {len(alertas)}\n\n")

        if alertas:
            f.write("Bloques con alerta:\n")
            for i, timestamp in alertas:
                f.write(f"- Bloque {i} con Timestamp: {timestamp}\n")
            f.write("\n")

        f.write("Promedios:\n")
        f.write(f"- Frecuencia: {promedio_frecuencia}\n")
        f.write(f"- Oxígeno: {promedio_oxigeno}\n")
        f.write(f"- Presión sistólica: {promedio_presion_1}\n")
        f.write(f"- Presión diastólica: {promedio_presion_2}\n")

    print('REPORTE GENERADO CON ÉXITO')            