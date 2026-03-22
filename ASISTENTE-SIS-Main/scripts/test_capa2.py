import requests

QUERY_URL = "http://localhost:8000/api/v1/asistente-virtual/query"

def test_llm():
    print("--- Test 3: LLM Generation (Capa 2) ---")
    payload = {
        "mensaje": "Cuéntame un poco sobre la historia de la UNETI y por qué es importante.",
        "tipo_entrada": "texto"
    }
    
    try:
        resp = requests.post(QUERY_URL, data=payload, timeout=60)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Respuesta del Asistente: {data['respuesta']}")
            print(f"Capa utilizada: {data['capa_utilizada']}")
            print(f"Confianza: {data['confianza']}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Fallo en la conexión: {e}")

if __name__ == "__main__":
    test_llm()
