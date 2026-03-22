import re
import asyncio
import httpx
import os
from typing import List, Dict

API_URL = "http://localhost:8000/api/v1/admin/faq/"
FILE_PATH = "FAQsUNETIDATASET1.txt"

def parse_faqs(file_path: str) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalizar saltos de línea y espacios
    content = content.replace('\r\n', '\n')
    
    # Dividir por categorías (bloques entre paréntesis al inicio de línea o tras saltos)
    categories = re.split(r'\n\s*\(([^)]+)\)', '\n' + content)
    
    faqs = []
    
    iter_cats = iter(categories)
    next(iter_cats, "") # Descartar primer fragmento
    
    while True:
        try:
            cat_name = next(iter_cats).strip()
            block_content = next(iter_cats)
            
            # Buscar fragmentos de preguntas: Numero. ¿...?
            q_blocks = re.split(r'\n\s*\d+\.\s+', '\n' + block_content)
            
            for qb in q_blocks:
                qb = qb.strip()
                if not qb:
                    continue
                
                # Buscar "Respuesta:"
                parts = re.split(r'\n\s*Respuesta:\s*', qb, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    pregunta = parts[0].replace('\n', ' ').strip()
                    respuesta = parts[1].strip().strip('"').strip()
                    
                    # Keywords simples
                    palabras_clave = [w.lower() for w in re.findall(r'\w{4,}', pregunta)]
                    
                    faqs.append({
                        "categoria": cat_name[:50], # Truncar por si acaso el ORM tiene límite
                        "pregunta_patron": pregunta,
                        "palabras_clave": list(set(palabras_clave))[:8],
                        "respuesta": respuesta,
                        "activo": True
                    })
        except StopIteration:
            break
            
    return faqs

async def seed_data(faqs: List[Dict]):
    print(f"Iniciando carga de {len(faqs)} FAQs...")
    async with httpx.AsyncClient() as client:
        # Primero limpiar o verificar si ya existen? 
        # Para simplificar, solo cargaremos las que den error o todas de nuevo si el DB lo permite.
        for faq in faqs:
            try:
                resp = await client.post(API_URL, json=faq, timeout=20.0)
                if resp.status_code in [200, 201]:
                    print(f"✅ OK: {faq['pregunta_patron'][:40]}...")
                else:
                    print(f"❌ ERR {resp.status_code}: {faq['pregunta_patron'][:40]}")
                    # Mostrar un poco del JSON enviado para debug si falla
                    if resp.status_code == 500:
                         print(f"   Payload: {faq['categoria']} | {len(faq['respuesta'])} chars")
            except Exception as e:
                print(f"🔥 Exc: {e}")

if __name__ == "__main__":
    if os.path.exists(FILE_PATH):
        dataset = parse_faqs(FILE_PATH)
        if dataset:
            asyncio.run(seed_data(dataset))
        else:
            print("No se extrajeron datos.")
    else:
        print("Archivo no encontrado.")
