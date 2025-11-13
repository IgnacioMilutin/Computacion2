import asyncio
import pdb

class ContadorAwaitable:
    """Un awaitable personalizado que cuenta hasta un número"""
    
    def __init__(self, hasta):
        self.hasta = hasta
        self.actual = 0
    
    def __await__(self):
        """Este método convierte el objeto en awaitable"""
        # Retornamos un generador que el event loop puede manejar
        while self.actual < self.hasta:
            self.actual += 1
            # yield None le dice al event loop: "pausa aquí y dame control después"
            yield
        return self.actual

async def usar_contador():
    print("Iniciando contador...")
    resultado = await ContadorAwaitable(5)
    print(f"Contador llegó a: {resultado}")
asyncio.run(usar_contador())