from multiprocessing import Process

def sumar(contador):
    for _ in range(100000):
        contador.value += 1  # condición de carrera

if __name__ == "__main__":
    from multiprocessing import Value
    contador = Value('i', 0)
    p1 = Process(target=sumar, args=(contador,))
    p2 = Process(target=sumar, args=(contador,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Valor final:", contador.value)  # Resultado incorrecto
