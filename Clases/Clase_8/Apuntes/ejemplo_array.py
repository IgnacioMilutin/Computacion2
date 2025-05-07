from multiprocessing import Process, Array

def rellenar(arr):
    for i in range(len(arr)):
        arr[i] = i * i

if __name__ == "__main__":
    datos = Array('i', 5)  # Array de 5 enteros
    p = Process(target=rellenar, args=(datos,))
    p.start()
    p.join()
    print(list(datos))  # [0, 1, 4, 9, 16]
