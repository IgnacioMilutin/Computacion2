from generador import proceso_generador
from multiprocessing import Process,Pipe,Queue,Semaphore
from analizador import proceso_analizador
from verificador import proceso_verificador
from verificar_cadena import verificador_cadena
from reporte import generador_reporte

def main():
    tipos=['frecuencia','presion','oxigeno']
    pipes=[]
    procesos_analizadores=[]
    queue=Queue()
    semaforo=Semaphore(0)

    for tipo in tipos:
        escritura,lectura=Pipe()
        pipes.append(escritura)
        p_analizador=Process(target=proceso_analizador,args=(tipo,lectura, queue, semaforo))
        procesos_analizadores.append(p_analizador)
        p_analizador.start()

    p_verificador=Process(target=proceso_verificador, args=(queue, semaforo, tipos))
    p_verificador.start()

    p_generador=Process(target=proceso_generador, args=(tipos,pipes))   
    p_generador.start() 

    print(" Procesando analisis biométricos\n\n")

    p_generador.join()

    for proceso in procesos_analizadores:
        proceso.join()
    p_verificador.join()

    print('PROCESAMIENTO FINALIZADO\n')
    
    while True:
        opcion=input("¿Desea verificar la integridad de la blockchain? (Y/N): ").strip()
        if opcion.lower()=='y':
            verificador_cadena()
            break
        elif opcion.lower()=='n':
            break
        else:
            print("Dato ingresado no válido. Ingrese 'Y' o 'N'.")

    while True:
        opcion = input("\n¿Desea un reporte de del analisis biometrico? (Y/N): ").strip()
        if opcion.lower()=='y':
            generador_reporte()
            break
        elif opcion.lower()=='n':
            break
        else:
            print("Dato ingresado no válido. Ingrese 'Y' o 'N'.")


if __name__ == "__main__":
    main()