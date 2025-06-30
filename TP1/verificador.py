import json
import hashlib
import queue as q

def calcular_hash(bloque):
    bloque=json.dumps(bloque,sort_keys=True).encode()
    return hashlib.sha256(bloque).hexdigest()

def prev_hash(blockchain):
    if blockchain:
        return blockchain[-1]['hash']
    else: return 0

def proceso_verificador(queue,semaforo,tipos):
    blockchain=[]
    archivo_blockchain='blockchain.json'
    fin=0

    
    while True:
        data={}
        for i in range(3):
            data_recibida=queue.get(timeout=5)
            if data_recibida.get('tipo')=='fin':
                fin+=1
                continue
            else:data[data_recibida['tipo']]=data_recibida
                
        if fin==3:
            break

        alerta=False

        for tipo,dato in data.items():
            valor = dato['valor']
            if tipo == "frecuencia" and valor >= 200:
                alerta = True
            elif tipo == "oxigeno" and not (90 <= valor <= 100):
                alerta = True
            elif tipo == "presion" and dato['valor'][0] >= 200:
                alerta = True

        timestamp=data['frecuencia']['timestamp']
                    
        for info in data.values():
            for clave in ['timestamp','tipo']:
                del info[clave]

        resultado={
            'timestamp':timestamp,
            'datos':data,
            'alerta':alerta,
            'prev_hash':prev_hash(blockchain)
        }

        resultado['hash']=calcular_hash(resultado)

        blockchain.append(resultado)

        with open(archivo_blockchain,"w") as archivo:
            json.dump(blockchain,archivo)

        print(f"Bloque {len(blockchain)-1} , Hash: {resultado['hash']} , Alerta: {resultado['alerta']}\n")

        for i in range(3):
            semaforo.release()

    
    queue.close()
    queue.join_thread()
