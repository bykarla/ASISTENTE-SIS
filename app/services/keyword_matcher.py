# ByKP: Motor de Búsqueda Rápida por Tags con NLP (Keyword Matcher)
# Sincronizado con Issue #2 (QA)
# Célula 04 - Asistente Virtual SIS-UNETI

import os
import re
import unicodedata
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def limpiar_texto_nlp(texto: str) -> set:
    """
    Aplica normalización UTF-8 e insensibilidad a tildes (NLP básico).
    Devuelve un set de palabras clave limpias.
    """
    if not texto:
        return set()
    
    # 1. Todo a minúsculas
    texto = texto.lower()
    
    # 2. Eliminar tildes (Normalización NFD)
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    
    # 3. Dejar solo letras y números
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    
    palabras = set(texto.split())
    # Stopwords
    stopwords = {"el", "la", "los", "las", "un", "una", "y", "o", "de", "en", "para", "por", "a", "con", "que", "como", "del", "al", "mi", "se"}
    return palabras - stopwords

def buscar_respuesta_faq(mensaje_usuario: str):
    """
    Se conecta a PostgreSQL y busca la FAQ con más coincidencias de tags.
    Detecta si la respuesta requiere IA Generativa.
    """
    palabras_usuario = limpiar_texto_nlp(mensaje_usuario)
    if not palabras_usuario:
        return None

    db_url = os.getenv("DATABASE_URL")
    mejor_faq = None
    max_coincidencias = 0

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consultamos FAQs activas
        cursor.execute("SELECT id, pregunta_patron, respuesta, palabras_clave, prioridad FROM asistente_virtual.asistente_conocimiento WHERE activo = true")
        faqs = cursor.fetchall()
        
        for faq in faqs:
            # Limpiamos los tags de la BD para que coincidan con la limpieza del usuario
            tags_limpios = set()
            for tag in faq['palabras_clave']:
                tags_limpios.update(limpiar_texto_nlp(tag))
            
            # Intersección: ¿Cuántas palabras coinciden exactamente?
            coincidencias = len(palabras_usuario.intersection(tags_limpios))
            
            # Priorizamos por coincidencias y luego por nivel de prioridad
            if coincidencias > max_coincidencias:
                max_coincidencias = coincidencias
                mejor_faq = faq
                
        if max_coincidencias > 0:
            respuesta_oficial = mejor_faq["respuesta"]
            
            # DETECCIÓN DE DEUDA TÉCNICA (Issue #2):
            requiere_ia = "[PENDIENTE GENERAR CON IA]" in respuesta_oficial
            
            return {
                "id": str(mejor_faq["id"]),
                "pregunta_match": mejor_faq["pregunta_patron"],
                "respuesta": respuesta_oficial,
                "tags": mejor_faq["palabras_clave"],
                "prioridad": mejor_faq.get("prioridad", 5),
                "confianza": min(0.99, max_coincidencias * 0.25),
                "requiere_generacion_ia": requiere_ia
            }
        return None

    except Exception as e:
        print(f"❌ Error en Keyword Matcher: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()