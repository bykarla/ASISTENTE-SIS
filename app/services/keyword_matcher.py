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
    """
    palabras_usuario = limpiar_texto(mensaje_usuario)
    if not palabras_usuario:
        return None

    mejor_faq = None
    max_coincidencias = 0

    try:
        # RealDictCursor devuelve los resultados como Diccionarios en lugar de Tuplas
        cursor = db_conn.cursor(cursor_factory=RealDictCursor)
        
        # Consultamos todas las FAQs activas
        cursor.execute("SELECT id, pregunta_patron, respuesta, palabras_clave FROM asistente_virtual.asistente_conocimiento WHERE activo = true")
        faqs = cursor.fetchall()
        
        for faq in faqs:
            # Procesamos las palabras clave de la BD: 
            # 1. Pasamos a minúsculas
            # 2. Quitamos acentos
            # 3. Dividimos frases en palabras individuales para mayor probabilidad de match
            tags_originales = faq['palabras_clave']
            tags_procesados = set()
            for tag in tags_originales:
                tag_limpio = quitar_acentos(tag.lower())
                # Si el tag tiene varias palabras (ej: 'nuevo ingreso'), lo dividimos
                for palabra in tag_limpio.split():
                    tags_procesados.add(palabra)
            
            # Intersección: ¿Cuántas palabras del usuario coinciden con los tags procesados?
            coincidencias = len(palabras_usuario.intersection(tags_procesados))
            
            if coincidencias > max_coincidencias:
                max_coincidencias = coincidencias
                mejor_faq = faq
                
        # Si encontramos al menos una coincidencia, devolvemos la respuesta
        if max_coincidencias > 0:
            # Umbral mínimo de confianza: 1 palabra suele ser suficiente para FAQs muy específicas
            return {
                "id": str(mejor_faq["id"]),
                "pregunta_match": mejor_faq["pregunta_patron"],
                "respuesta": mejor_faq["respuesta"],
                "tags": mejor_faq["palabras_clave"],
                # Cálculo de confianza simple (cada coincidencia suma 40% hasta un tope de 99%)
                "confianza": min(0.99, max_coincidencias * 0.40) 
            }
        return None

    except Exception as e:
        print(f"❌ Error en Keyword Matcher: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()