from multiprocessing import Pool

def cuadrado(x):
    return x * x

if __name__ == "__main__":
    numeros = [1, 2, 3, 4, 5]
    with Pool(processes=4) as pool:
        resultados = pool.map(cuadrado, numeros)
    print(resultados)  # [1, 4, 9, 16, 25]
