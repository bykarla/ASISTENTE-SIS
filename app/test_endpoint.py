import httpx
import asyncio

async def test_query():
    url = "http://localhost:8000/api/v1/asistente-virtual/query"
    data = {
        "mensaje": "hola",
        "tipo_entrada": "texto"
    }
    
    print(f"Enviando petición a {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, data=data, timeout=30.0)
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_query())
