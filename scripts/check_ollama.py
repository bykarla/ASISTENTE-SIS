import httpx
import asyncio
from app.core.config import settings

async def test_ollama():
    print(f"Testing OLLAMA_URL: {settings.OLLAMA_URL}")
    print(f"Testing LLM_MODEL: {settings.LLM_MODEL}")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            print(f"Status Tags: {resp.status_code}")
            print(f"Tags Response: {resp.json()}")
            
            # Test generate
            print("\nTesting Generate...")
            resp_gen = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": settings.LLM_MODEL,
                    "prompt": "Hola",
                    "stream": False
                },
                timeout=60.0
            )
            print(f"Status Generate: {resp_gen.status_code}")
            if resp_gen.status_code == 200:
                print(f"Generate Response: {resp_gen.json().get('response', 'NO RESPONSE')}")
            else:
                print(f"Generate Error: {resp_gen.text}")
            
        except Exception as e:
            import traceback
            print(f"CONNECTION ERROR: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ollama())
