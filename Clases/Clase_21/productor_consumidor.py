import asyncio
import random

async def productor(queue, id_productor, num_items):
    """Produce items y los pone en la cola"""
    for i in range(num_items):
        # Simular trabajo variable
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        item = f"Item-{id_productor}-{i}"
        await queue.put(item)
        print(f"🏭 Productor {id_productor} creó: {item}")
    
    print(f"✅ Productor {id_productor} terminó")

async def consumidor(queue, id_consumidor):
    """Consume items de la cola"""
    while True:
        # Esperar hasta que haya un item
        item = await queue.get()
        
        # None es la señal de terminar
        if item is None:
            queue.task_done()
            break
        
        # Simular procesamiento
        await asyncio.sleep(random.uniform(0.2, 0.8))
        print(f"  🔧 Consumidor {id_consumidor} procesó: {item}")
        
        # Marcar como completado
        queue.task_done()
    
    print(f"✅ Consumidor {id_consumidor} terminó")

async def main():
    # Cola con capacidad limitada (backpressure)
    queue = asyncio.Queue(maxsize=100)
    
    # Crear productores
    num_productores = 3
    items_por_productor = 4
    productores = [
        productor(queue, i, items_por_productor)
        for i in range(num_productores)
    ]
    
    # Crear consumidores
    num_consumidores = 2
    consumidores = [
        consumidor(queue, i)
        for i in range(num_consumidores)
    ]
    
    # Ejecutar todos los productores
    await asyncio.gather(*productores)
    
    
    
    # Enviar señal de terminación a consumidores
    for _ in range(num_consumidores):
        await queue.put(None)
    
    # Esperar a que terminen los consumidores
    await asyncio.gather(*consumidores)

    # Esperar a que se procesen todos los items
    await queue.join()
    
    print("\n🎉 Pipeline completado")

if __name__ == "__main__":
    asyncio.run(main())