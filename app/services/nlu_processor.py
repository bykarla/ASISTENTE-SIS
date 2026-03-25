# ByKP: Procesador NLU (Natural Language Understanding) Ligero
# Ruta: app/services/nlu_processor.py
# Célula 04 - Asistente Virtual SIS-UNETI 2026
# Este módulo usa spaCy para detectar intenciones complejas sin gastar RAM en el LLM.

import spacy
from typing import Dict, List, Optional

# Intentamos cargar el modelo en español ligero. 
# (Si no está, el lifespan de main.py deberá descargarlo: python -m spacy download es_core_news_sm)
try:
    nlp = spacy.load("es_core_news_sm")
    print("✅ [NLU] Modelo spaCy 'es_core_news_sm' cargado correctamente.")
except OSError:
    print("⚠️ [NLU] Modelo spaCy no encontrado. Se requiere ejecutar: python -m spacy download es_core_news_sm")
    nlp = None

# ============================================================================
# DICCIONARIO DE INTENCIONES (Reglas Heurísticas + NLP)
# ============================================================================
# Mapeo de intenciones clave del sistema SIS-UNETI
INTENCIONES_SISTEMA = {
    "consultar_notas": ["nota", "calificacion", "promedio", "record", "cuanto saque"],
    "requisitos_inscripcion": ["inscribir", "requisito", "documento", "carpeta", "opsu"],
    "problema_acceso": ["clave", "contraseña", "bloqueado", "acceso", "login", "entrar"],
    "solicitar_humano": ["humano", "asesor", "persona", "operador", "coordinador", "hablar con alguien"]
}

def detectar_intencion(mensaje: str) -> Optional[str]:
    """
    Analiza el mensaje usando spaCy para encontrar la intención principal.
    Retorna el código de la intención (ej. 'consultar_notas') o None si no está seguro.
    """
    if not nlp:
        return None
        
    doc = nlp(mensaje.lower())
    
    # 1. Extraemos los 'lemas' (raíces de las palabras, ej: 'inscribí' -> 'inscribir')
    lemas_usuario = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    
    # 2. Comparamos los lemas con nuestro diccionario de intenciones
    mejor_intencion = None
    max_coincidencias = 0
    
    for intencion, palabras_clave in INTENCIONES_SISTEMA.items():
        coincidencias = len(set(lemas_usuario).intersection(set(palabras_clave)))
        
        if coincidencias > max_coincidencias:
            max_coincidencias = coincidencias
            mejor_intencion = intencion
            
    # Solo devolvemos la intención si estamos relativamente seguros (al menos 1 coincidencia fuerte)
    if max_coincidencias >= 1:
        return mejor_intencion
        
    return None

def extraer_entidades(mensaje: str) -> Dict[str, List[str]]:
    """
    Extrae entidades nombradas (Lugares, Personas, Fechas) del mensaje.
    Útil para saber si el estudiante mencionó una sede específica o una fecha.
    """
    if not nlp:
        return {}
        
    doc = nlp(mensaje)
    entidades = {
        "lugares": [ent.text for ent in doc.ents if ent.label_ == "LOC"],
        "fechas": [ent.text for ent in doc.ents if ent.label_ == "DATE"],
        "personas": [ent.text for ent in doc.ents if ent.label_ == "PER"]
    }
    
    return entidades