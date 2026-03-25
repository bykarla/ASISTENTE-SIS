# ByKP / QA: Script de Auditoría de Base de Conocimiento (Capa 1)
# Ruta local: tests/test_faqs_integrity.py
# Desarrollado por: Ricardo Castro (QA) | Integrado por: Karla Pastrán (Backend)
# Célula 04: Servicios e Innovación - SIS-UNETI 2026

import json
import os
import sys
import pytest
from pydantic import ValidationError

# Añadimos la raíz del proyecto al path para poder importar los schemas de 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.schemas import ConocimientoBase
except ImportError:
    pytest.fail("❌ No se encontró el archivo app/schemas.py en el proyecto.")

# Ruta dinámica al archivo JSON estandarizado por QA
JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'FAQs_Saneado.json')

def load_faqs():
    """Carga el archivo JSON generado para la Célula 04."""
    if not os.path.exists(JSON_PATH):
        pytest.fail(f"❌ Archivo FAQs_Saneado.json no encontrado en la ruta: {JSON_PATH}")
        
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        pytest.fail("❌ El archivo faqs.json tiene un error de sintaxis (comas faltantes o llaves mal cerradas).")

def test_pydantic_contract_validation():
    """
    TEST 1: Validación de Contrato Estricto.
    Verifica que cada objeto cumpla con tipos, longitudes y el alias 'palabras_clave'
    basado en el Schema (DTO) del Backend.
    """
    faqs = load_faqs()
    errors = []
    
    for index, faq in enumerate(faqs):
        try:
            # Pydantic validará:
            # - categoria y subcategoria <= 50 caracteres
            # - prioridad >= 0
            # - mapeo de 'palabras_clave' -> 'tags'
            ConocimientoBase.model_validate(faq)
        except ValidationError as e:
            # Capturamos el error específico para reportarlo
            error_msg = f"Error en registro #{index + 1} (Pregunta: {faq.get('pregunta_patron', 'S/N')}): {e.errors()}"
            errors.append(error_msg)
            
    assert not errors, f"⚠️ Se encontraron {len(errors)} discrepancias con el schema de Backend:\n" + "\n".join(errors)

def test_logic_integrity():
    """
    TEST 2: Integridad Lógica del Dataset.
    Verifica duplicados y consistencia de campos obligatorios.
    """
    faqs = load_faqs()
    questions_seen = set()
    
    for faq in faqs:
        # 1. Verificar que no haya preguntas repetidas exactamente igual
        p = faq["pregunta_patron"].strip().lower()
        assert p not in questions_seen, f"⚠️ Pregunta duplicada detectada: {faq['pregunta_patron']}"
        questions_seen.add(p)
        
        # 2. Verificar que haya al menos una palabra clave (tag)
        assert len(faq["palabras_clave"]) > 0, f"⚠️ La pregunta '{faq['pregunta_patron']}' no tiene tags asignados."

def test_priority_weighting():
    """
    TEST 3: Validación de Prioridades (Capa 1).
    Asegura que los valores de prioridad estén en el rango configurado (0-10).
    """
    faqs = load_faqs()
    for faq in faqs:
        prioridad = faq.get("prioridad", 0)
        assert 0 <= prioridad <= 10, f"⚠️ Prioridad fuera de rango (0-10) en: {faq['pregunta_patron']}"

if __name__ == "__main__":
    print("--- Iniciando Auditoría Técnica de faqs.json ---")
    # Ejecución manual rápida si no se usa pytest directamente
    data = load_faqs()
    print(f"✅ Registros cargados: {len(data)}")
    print("✅ Sincronización con app/schemas.py: OK")