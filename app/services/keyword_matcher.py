import re
import unicodedata
from psycopg2.extras import RealDictCursor

def quitar_acentos(texto: str) -> str:
    """Elimina acentos y tildes de un string en español."""
    return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def limpiar_texto(texto: str) -> set:
    """Limpia el texto del usuario y devuelve un set de palabras clave sin acentos."""
    texto = texto.lower()
    texto = quitar_acentos(texto)
    # Eliminar signos de puntuación básicos
    texto = re.sub(r'[^\w\s]', '', texto)
    palabras = set(texto.split())
    # Ignorar conectores comunes (stopwords) sin acentos
    stopwords = {"el", "la", "los", "las", "un", "una", "y", "o", "de", "en", "para", "por", "a", "con", "que", "como", "del", "al", "mi"}
    return palabras - stopwords

def buscar_respuesta_faq(db_conn, mensaje_usuario: str):
    """
    Busca la FAQ con más coincidencias de tags en la conexión de BD proporcionada.
    Incluye una Capa 0 de saludos básicos.
    """
    # --- Capa 0: Saludos Directos ---
    saludos = {"hola", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos"}
    palabras_usuario = limpiar_texto(mensaje_usuario)
    
    if any(s in palabras_usuario for s in saludos) and len(palabras_usuario) <= 2:
        return {
            "id": "greeting_0",
            "pregunta_match": "saludo_usuario",
            "respuesta": "¡Hola! Soy el Asistente Virtual de la UNETI. 😊 ¿En qué puedo ayudarte hoy con respecto a inscripciones, materias o procesos académicos?",
            "tags": ["saludo"],
            "confianza": 1.0
        }

    if not palabras_usuario:
        return None

    mejor_faq = None
    max_coincidencias = 0

    try:
        cursor = db_conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, pregunta_patron, respuesta, palabras_clave FROM asistente_virtual.asistente_conocimiento WHERE activo = true")
        faqs = cursor.fetchall()
        
        for faq in faqs:
            tags_originales = faq['palabras_clave']
            tags_procesados = set()
            for tag in tags_originales:
                tag_limpio = quitar_acentos(tag.lower())
                for palabra in tag_limpio.split():
                    tags_procesados.add(palabra)
            
            coincidencias = len(palabras_usuario.intersection(tags_procesados))
            
            if coincidencias > max_coincidencias:
                max_coincidencias = coincidencias
                mejor_faq = faq
                
        # --- Mejora: Umbral de confianza dinámico ---
        # Si el usuario escribió mucho, exigimos al menos 2 coincidencias para evitar la Capa 1 "ruidosa"
        umbral_minimo = 2 if len(palabras_usuario) > 3 else 1

        if max_coincidencias >= umbral_minimo:
            return {
                "id": str(mejor_faq["id"]),
                "pregunta_match": mejor_faq["pregunta_patron"],
                "respuesta": mejor_faq["respuesta"],
                "tags": mejor_faq["palabras_clave"],
                "confianza": min(0.99, max_coincidencias * 0.35) 
            }
        return None

    except Exception as e:
        print(f"❌ Error en Keyword Matcher: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()