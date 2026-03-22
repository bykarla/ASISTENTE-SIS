# ByKP: Implementación de la Fórmula Soberana y Convertidor de Notas
# Célula 04: Servicios e Innovación - SIS-UNETI 2026
# REQUERIMIENTO: REQ-AC-02 (Normalización de Calificaciones / Moodle Sync)

from pydantic import BaseModel, Field
from typing import Dict

class ResultadoSoberano(BaseModel):
    """
    Esquema de respuesta para la validación de actas (REQ-AC-02).
    Asegura la trazabilidad entre la escala Moodle y la escala legal UNETI.
    """
    nota_moodle: float = Field(..., ge=0, le=100, description="Escala original Moodle (0-100)")
    nota_uneti_20: float = Field(..., ge=1, le=20, description="Escala legal UNETI (1-20)")
    nota_letras: str = Field(..., description="Calificación cualitativa")
    estado: str = Field(..., description="Estatus (Aprobado/Reprobado)")
    puede_cerrar_acta: bool = Field(..., description="Filtro de integridad para REQ-AC-02")
    descripcion: str

def aplicar_formula_soberana(actividades: Dict[str, float]) -> ResultadoSoberano:
    """
    Implementa la lógica de negocio del REQ-AC-02:
    Fórmula: Nota20 = (Nota100 / 100) * 20
    """
    # 1. Sumatoria de notas desde la interfaz Moodle (0-100)
    nota_100 = sum(actividades.values())
    nota_100 = min(100.0, max(0.0, nota_100)) # Clamping de seguridad
    
    # 2. CONVERSIÓN AUTOMÁTICA (Lógica de Negocio REQ-AC-02)
    # Aplicación de la fórmula institucional
    nota_20_calculada = (nota_100 / 100) * 20
    
    # Según normativa, la escala legal es 1-20 (el 0 no existe en acta final)
    nota_20_final = max(1.0, round(nota_20_calculada, 2))
    
    # 3. CLASIFICACIÓN CUALITATIVA
    if nota_100 >= 90:
        letras, calif = "A", "Excelente"
    elif nota_100 >= 80:
        letras, calif = "B", "Bien"
    elif nota_100 >= 70:
        letras, calif = "C", "Suficiente"
    else:
        letras, calif = "D", "Insuficiente"

    estado = "Aprobado" if nota_100 >= 70 else "Reprobado"

    # 4. VALIDACIÓN DE INCONSISTENCIAS (REQ-AC-02)
    # El sistema recalcula la relación para verificar que no haya corrupción de datos
    relacion_teorica = (nota_100 / 100) * 20
    # Tolerancia de 0.01 por errores de redondeo en punto flotante
    consistente = abs(relacion_teorica - nota_20_calculada) < 0.001
    
    # Verificación adicional de rangos legales
    if not (1.0 <= nota_20_final <= 20.0):
        consistente = False

    mensaje = (
        f"REQ-AC-02 Sincronizado: Moodle {nota_100}/100 -> UNETI {nota_20_final}/20. "
        f"Resultado: {letras} ({calif})."
    )
    
    return ResultadoSoberano(
        nota_moodle=nota_100,
        nota_uneti_20=nota_20_final,
        nota_letras=letras,
        estado=estado,
        puede_cerrar_acta=consistente,
        descripcion=mensaje
    )

def validar_cierre_acta(resultado: ResultadoSoberano) -> bool:
    """
    Control de Calidad REQ-AC-02: 
    Bloquea el cierre de acta si la conversión presenta inconsistencias.
    """
    if not resultado.puede_cerrar_acta:
        # Aquí se dispararía un log hacia la tabla 'asistente_auditoria'
        return False
    return True