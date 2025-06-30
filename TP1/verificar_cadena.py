import hashlib
import json

def calcular_hash(bloque):
    bloque=json.dumps(bloque,sort_keys=True).encode()
    return hashlib.sha256(bloque).hexdigest()

def verificador_cadena():
    archivo_blockchain='blockchain.json'
    with open(archivo_blockchain,'r') as archivo:
        blockchain=json.load(archivo)

    errores=0
    bloques_erroneos=[]

    for i in range(len(blockchain)-1,-1,-1):
        bloque = blockchain[i]
        if i>0:
            bloque_anterior=blockchain[i-1]
            bloque_anterior_hash=bloque_anterior.get('hash')
        else:
            bloque_anterior=None

        bloque_actual_hash=bloque.pop('hash')
        bloque_actual_prev_hash=bloque.get('prev_hash')

        hash_recalculado=calcular_hash(bloque)

        if bloque_actual_hash!=hash_recalculado:
            errores+=1
            bloques_erroneos.append(i)

        if bloque_actual_prev_hash!=bloque_anterior_hash and bloque_anterior is not None:
            errores+=1
            bloques_erroneos.append(i)

    if errores==0:
        print('Blockchain verificada, No hay errores')
        return errores
    else:
        print(f'Blockchain verificada, contiene errores. Errores en bloque: {bloques_erroneos}')
        return errores,bloques_erroneos
