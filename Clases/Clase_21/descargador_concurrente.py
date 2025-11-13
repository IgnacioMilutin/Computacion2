import asyncio
import aiohttp
import aiofiles
from pathlib import Path

async def descargar_imagen(session, url, nombre_archivo):
    """Descarga una imagen y la guarda en disco"""
    print(f"📥 Descargando {nombre_archivo}...")
    
    async with session.get(url) as response:
        if response.status == 200:
            # Leer el contenido como bytes
            contenido = await response.read()
            
            # Escribir el archivo de forma asíncrona
            async with aiofiles.open(f"descargas/{nombre_archivo}", "wb") as f:
                await f.write(contenido)
            
            print(f"✅ {nombre_archivo} descargado ({len(contenido)} bytes)")
        else:
            print(f"❌ Error descargando {nombre_archivo}: {response.status}")

async def main():
    # Crear directorio si no existe
    Path("descargas").mkdir(exist_ok=True)
    
    # Lista de imágenes a descargar
    imagenes = [
        ("https://picsum.photos/400/300", "imagen1.jpg"),
        ("https://picsum.photos/500/400", "imagen2.jpg"),
        ("https://picsum.photos/600/400", "imagen3.jpg"),
        ("https://picsum.photos/300/500", "imagen4.jpg"),
    ]
    
    # Crear una sesión compartida (más eficiente)
    async with aiohttp.ClientSession() as session:
        # Crear todas las tareas
        tareas = [
            descargar_imagen(session, url, nombre)
            for url, nombre in imagenes
        ]
        
        # Ejecutar concurrentemente
        await asyncio.gather(*tareas)
    
    print("\n🎉 Todas las descargas completadas")

if __name__ == "__main__":
    asyncio.run(main())