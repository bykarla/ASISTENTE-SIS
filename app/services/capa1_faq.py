from typing import Optional
from sqlalchemy.orm import Session
from app.models.orm import AsistenteConocimiento
import re

def buscar_faq(mensaje: str, db: Session) -> tuple[Optional[str], float, Optional[str]]:
    """
    Retorna (respuesta, confianza, fuente) si encuentra match por keywords.
    """
    # Normalizar mensaje (limpiar puntuación y a minúsculas)
    mensaje_limpio = re.sub(r'[^\w\s]', '', mensaje.lower())
    palabras = [w for w in mensaje_limpio.split() if len(w) > 2]
    
    mejores = []
    faqs = db.query(AsistenteConocimiento).filter(AsistenteConocimiento.activo == True).all()
    
    for faq in faqs:
        pregunta_baja = faq.pregunta_patron.lower()
        keywords = [k.lower() for k in faq.palabras_clave]
        
        coincidencias = 0
        # 1. Buscar en palabras clave
        for kw in keywords:
            if any(kw in p or p in kw for p in palabras):
                coincidencias += 1
        
        # 2. Buscar en la pregunta patrón directamente
        match_directo = sum(1 for p in palabras if p in pregunta_baja)
        
        score_kw = coincidencias / len(keywords) if keywords else 0
        score_pattern = match_directo / len(pregunta_baja.split()) if pregunta_baja else 0
        
        # Score final combinado
        final_score = max(score_kw, score_pattern)
        
        if final_score > 0:
            mejores.append((final_score, faq.respuesta, faq.pregunta_patron))
            
    if mejores:
        mejores.sort(reverse=True, key=lambda x: x[0])
        score, respuesta, fuente = mejores[0]
        # Con 0.25 (1 word match de 4, o similar) ya es suficiente para FAQ
        if score >= 0.25:
            return respuesta, score, fuente
    return None, 0.0, None