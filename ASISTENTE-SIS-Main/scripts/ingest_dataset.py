import re
import asyncio
import httpx
import os
from typing import List, Dict

# Configuración básica
API_URL = "http://localhost:8000/api/v1/admin/faq/"
FILE_PATH = "FAQsUNETIDATASET1.txt"

def parse_faqs(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Dividir por categorías (bloques entre paréntesis)
    categories = re.split(r'\(([^)]+)\)', content)
    
    faqs = []
    current_category = "General"
    
    # El split devuelve [texto_antes, cat1, texto1, cat2, texto2...]
    iter_cats = iter(categories)
    first_block = next(iter_cats, "") # Ignorar posible texto antes del primer paréntesis
    
    while True:
        try:
            cat_name = next(iter_cats).strip()
            block_content = next(iter_cats)
            
            # Buscar patrones de Pregunta: Numero. ¿Pregunta?
            # Y Respuesta: "Contenido"
            q_blocks = re.split(r'\d+\.\s+', block_content)
            
            for qb in q_blocks:
                if not qb.strip():
                    continue
                
                # Separar pregunta de respuesta
                parts = re.split(r'Respuesta:\s*', qb, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    pregunta = parts[0].strip()
                    # Limpiar la respuesta de comillas iniciales/finales y espacios
                    respuesta = parts[1].strip().strip('"')
                    
                    # Generar palabras clave simples (mínimo 3 caracteres)
                    palabras_clave = [w.lower() for w in re.findall(r'\w{4,}', pregunta)]
                    
                    faqs.append({
                        "categoria": cat_name,
                        "pregunta_patron": pregunta,
                        "palabras_clave": list(set(palabras_clave))[:10], # máx 10 keywords
                        "respuesta": respuesta,
                        "activo": True
                    })
        except StopIteration:
            break
            
    return faqs

async def seed_data(faqs: List[Dict]):
    print(f"Iniciando carga de {len(faqs)} FAQs...")
    async with httpx.AsyncClient() as client:
        for faq in faqs:
            try:
                resp = await client.post(API_URL, json=faq, timeout=10.0)
                if resp.status_code == 200 or resp.status_code == 201:
                    print(f"✅ Cargada: {faq['pregunta_patron'][:50]}...")
                else:
                    print(f"❌ Error ({resp.status_code}) en: {faq['pregunta_patron'][:50]}")
                    print(f"Detalle: {resp.text}")
            except Exception as e:
                print(f"🔥 Excepción: {e}")

if __name__ == "__main__":
    if os.path.exists(FILE_PATH):
        dataset = parse_faqs(FILE_PATH)
        if dataset:
            asyncio.run(seed_data(dataset))
        else:
            print("No se pudieron extraer FAQs del archivo.")
    else:
        print(f"Archivo no encontrado: {FILE_PATH}")
