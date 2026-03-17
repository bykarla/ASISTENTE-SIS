# ByKP: Motor de Búsqueda Rápida por Tags (Keyword Matcher)
# app/services/keyword_matcher.py
# Célula 04 - Asistente Virtual SIS-UNETI

import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def limpiar_texto(texto: str) -> set:
    """Limpia el texto del usuario y devuelve un set de palabras clave."""
    texto = texto.lower()
    # Eliminar signos de puntuación básicos
    texto = re.sub(r'[^\w\s]', '', texto)
    palabras = set(texto.split())
    # Ignorar conectores comunes (stopwords)
    stopwords = {"el", "la", "los", "las", "un", "una", "y", "o", "de", "en", "para", "por", "a", "con", "que", "como", "del", "al", "mi"}
    return palabras - stopwords

def buscar_respuesta_faq(mensaje_usuario: str):
    """
    Se conecta a PostgreSQL y busca la FAQ con más coincidencias de tags.
    """
    palabras_usuario = limpiar_texto(mensaje_usuario)
    if not palabras_usuario:
        return None

    db_url = os.getenv("DATABASE_URL")
    mejor_faq = None
    max_coincidencias = 0

    try:
        conn = psycopg2.connect(db_url)
        # RealDictCursor devuelve los resultados como Diccionarios en lugar de Tuplas
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Consultamos todas las FAQs activas
        cursor.execute("SELECT id, pregunta_patron, respuesta, palabras_clave FROM asistente_virtual.asistente_conocimiento WHERE activo = true")
        faqs = cursor.fetchall()
        
        for faq in faqs:
            # Convertimos los tags de la BD a minúsculas
            tags = set([tag.lower() for tag in faq['palabras_clave']])
            
            # Intersección: ¿Cuántas palabras del usuario coinciden con los tags de esta pregunta?
            coincidencias = len(palabras_usuario.intersection(tags))
            
            if coincidencias > max_coincidencias:
                max_coincidencias = coincidencias
                mejor_faq = faq
                
        # Si encontramos al menos una coincidencia, devolvemos la respuesta
        if max_coincidencias > 0:
            return {
                "id": str(mejor_faq["id"]),
                "pregunta_match": mejor_faq["pregunta_patron"],
                "respuesta": mejor_faq["respuesta"],
                "tags": mejor_faq["palabras_clave"],
                # Cálculo de confianza simple (cada coincidencia suma 25% hasta un tope de 99%)
                "confianza": min(0.99, max_coincidencias * 0.25) 
            }
        return None

    except Exception as e:
        print(f"❌ Error en Keyword Matcher: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()