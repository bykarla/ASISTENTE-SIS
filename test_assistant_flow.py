import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from app.services.keyword_matcher import buscar_respuesta_faq
from app.services.llm_service import responder_con_ia
from app.config import settings

async def test_flow():
    print("--- Test Capa 1: FAQ ---")
    # Intentamos conectar a la BD local (puerto 5433 mapeado en host)
    try:
        conn = psycopg2.connect("postgresql://admin_uneti:superpassword2026@localhost:5433/asistente_virtual")
        
        # Caso 1: Match directo
        res1 = buscar_respuesta_faq(conn, "¿cuanto cuesta estudiar?")
        print(f"Pregunta: ¿cuanto cuesta estudiar?\nRespuesta: {res1['respuesta'] if res1 else 'No match'}\nCapa: {res1['capa_utilizada'] if res1 and 'capa_utilizada' in res1 else '1'}\n")
        
        # Caso 2: Match por tags
        res2 = buscar_respuesta_faq(conn, "requisitos para inscripcion")
        print(f"Pregunta: requisitos para inscripcion\nRespuesta: {res2['respuesta'] if res2 else 'No match'}\n")
        
    except Exception as e:
        print(f"Error conectando a BD: {e}")

    print("\n--- Test Capa 2: IA ---")
    # Caso 3: Pregunta compleja para LLM
    try:
        res3 = await responder_con_ia("¿Como puedo cambiar de carrera?", "test-session-123")
        print(f"Pregunta: ¿Como puedo cambiar de carrera?\nRespuesta: {res3['respuesta']}\nFuente: {res3['fuente']}\n")
    except Exception as e:
        print(f"Error en LLM: {e}")

if __name__ == "__main__":
    asyncio.run(test_flow())
