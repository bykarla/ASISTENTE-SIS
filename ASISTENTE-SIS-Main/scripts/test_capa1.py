import requests
import uuid

BASE_URL = "http://localhost:8000"
ADMIN_FAQ_URL = f"{BASE_URL}/api/v1/admin/faq/"
QUERY_URL = f"{BASE_URL}/api/v1/asistente-virtual/query"

def seed_and_test():
    print("--- Seeding FAQ ---")
    faq_data = {
        "pregunta_patron": "¿Cuáles son los requisitos de inscripción?",
        "respuesta": "Los requisitos son: Título de Bachiller, Partida de Nacimiento y Cédula de Identidad.",
        "palabras_clave": ["inscripcion", "requisitos", "documentos", "bachiller"],
        "categoria": "GENERAL",
        "activo": True
    }
    
    resp_admin = requests.post(ADMIN_FAQ_URL, json=faq_data)
    if resp_admin.status_code == 200:
        print("FAQ creada exitosamente.")
    else:
        print(f"Error creando FAQ: {resp_admin.text}")
        return

    print("\n--- Test 2: FAQ Key-word match (Capa 1) ---")
    payload = {
        "mensaje": "Hola, ¿que requisitos necesito para la inscripcion?",
        "tipo_entrada": "texto"
    }
    
    resp_query = requests.post(QUERY_URL, data=payload)
    print(f"Status Code: {resp_query.status_code}")
    if resp_query.status_code == 200:
        data = resp_query.json()
        print(f"Respuesta del Asistente: {data['respuesta']}")
        print(f"Capa utilizada: {data['capa_utilizada']}")
        print(f"Confianza: {data['confianza']}")
    else:
        print(f"Error en consulta: {resp_query.text}")

if __name__ == "__main__":
    seed_and_test()
