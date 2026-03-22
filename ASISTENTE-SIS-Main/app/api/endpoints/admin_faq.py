from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.request_response import FAQCreate, FAQOut
from app.models.orm import AsistenteConocimiento
from app.core.database import SessionLocal
from uuid import UUID

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FAQOut)
def crear_faq(faq: FAQCreate, db: Session = Depends(get_db)):
    db_faq = AsistenteConocimiento(**faq.model_dump())
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@router.get("/", response_model=list[FAQOut])
def listar_faqs(db: Session = Depends(get_db)):
    return db.query(AsistenteConocimiento).filter(AsistenteConocimiento.activo == True).all()

@router.get("/{faq_id}", response_model=FAQOut)
def obtener_faq(faq_id: UUID, db: Session = Depends(get_db)):
    faq = db.get(AsistenteConocimiento, faq_id)
    if not faq:
        raise HTTPException(404, "FAQ no encontrado")
    return faq

@router.put("/{faq_id}", response_model=FAQOut)
def actualizar_faq(faq_id: UUID, faq: FAQCreate, db: Session = Depends(get_db)):
    db_faq = db.get(AsistenteConocimiento, faq_id)
    if not db_faq:
        raise HTTPException(404, "FAQ no encontrado")
    for key, value in faq.model_dump().items():
        setattr(db_faq, key, value)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@router.delete("/{faq_id}")
def eliminar_faq(faq_id: UUID, db: Session = Depends(get_db)):
    db_faq = db.get(AsistenteConocimiento, faq_id)
    if not db_faq:
        raise HTTPException(404, "FAQ no encontrado")
    db.delete(db_faq)
    db.commit()
    return {"ok": True}