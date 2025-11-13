import asyncio
import aiohttp
from datetime import datetime

async def consultar_api(session, nombre, url, timeout_segundos=5):
    """Consulta una API con timeout"""
    try:
        inicio = datetime.now()
        
        # timeout_segundos aplica a toda la operación
        timeout = aiohttp.ClientTimeout(total=timeout_segundos)
        
        async with session.get(url, timeout=timeout) as response:
            datos = await response.json()
            
            duracion = (datetime.now() - inicio).total_seconds()
            print(f"✅ {nombre}: {response.status} ({duracion:.2f}s)")
            return {"api": nombre, "datos": datos, "duracion": duracion}
            
    except asyncio.TimeoutError:
        print(f"⏱️  {nombre}: Timeout después de {timeout_segundos}s")
        return {"api": nombre, "error": "timeout"}
        
    except Exception as e:
        print(f"❌ {nombre}: Error - {e}")
        return {"api": nombre, "error": str(e)}

async def main():
    apis = [
        ("JSONPlaceholder", "https://jsonplaceholder.typicode.com/posts/1"),
        ("GitHub", "https://api.github.com/users/github"),
        ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
        # Esta es lenta a propósito
        ("HTTPBin Delay", "https://httpbin.org/delay/10"),
    ]
    
    async with aiohttp.ClientSession() as session:
        tareas = [
            consultar_api(session, nombre, url, timeout_segundos=3)
            for nombre, url in apis
        ]
        
        resultados = await asyncio.gather(*tareas)
    
    print("\n📊 Resumen:")
    for resultado in resultados:
        print(f"  {resultado['api']}: {resultado.get('error', 'OK')}")

if __name__ == "__main__":
    asyncio.run(main())