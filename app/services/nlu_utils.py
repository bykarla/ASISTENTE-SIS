import spacy
from typing import Tuple, Optional
import re

# Cargar modelo de español de forma perezosa
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("es_core_news_sm")
    return _nlp

# Clasificador simple basado en reglas/palabras clave para intenciones
INTENT_PATTERNS = {
    "consultar_notas": ["nota", "notas", "calificación", "calificaciones", "récord", "promedio"],
    "inscripcion": ["inscripción", "inscribir", "matrícula", "periodo"],
    "tramite": ["trámite", "constancia", "certificado", "solicitar"],
    "horario": ["horario", "atención", "horas"],
    "prelacion": ["prelación", "prerrequisito", "requisito", "puedo inscribir"],
    "expediente": ["expediente", "documento", "pendiente"],
    "carnet": ["carnet", "qr", "identificación"],
    "arancel": ["costo", "pago", "arancel", "inscripción"],
    "saludo": ["hola", "buenos días", "buenas tardes", "qué tal"],
    "despedida": ["adiós", "chao", "hasta luego", "gracias"],
}

def detectar_intencion(texto: str) -> Tuple[str, float]:
    doc = get_nlp()(texto.lower())
    # Extraer lemas para mejor matching
    lemas = [token.lemma_ for token in doc]
    texto_lemas = " ".join(lemas)
    max_score = 0.0
    mejor_intencion = "fuera_de_alcance"
    for intent, keywords in INTENT_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in texto_lemas or kw in texto.lower())
        if score > max_score:
            max_score = score
            mejor_intencion = intent
    # Normalizar score (máximo posible = len(keywords), pero usamos proporción simple)
    # Para simplificar, devolvemos un score basado en cantidad de keywords encontradas
    # y un umbral.
    if max_score == 0:
        return "fuera_de_alcance", 0.0
    return mejor_intencion, min(max_score / 3, 1.0)  # max 1.0

def extraer_entidades(texto: str):
    doc = get_nlp()(texto)
    entidades = {}
    for ent in doc.ents:
        if ent.label_ in ["PER", "MISC"]:
            continue  # filtrar personas
        entidades[ent.label_] = ent.text
    # Extraer números de cédula (patrón simple)
    cedula = re.search(r'\b[VEJ]\-?\d{5,9}\b', texto, re.IGNORECASE)
    if cedula:
        entidades["CEDULA"] = cedula.group()
    return entidades