from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Literal
from datetime import date


# ─────────────────────────
# FILTROS DE ENTRADA
# ─────────────────────────

class ReportesFiltros(BaseModel):
    """
    Filtros enviados desde el frontend.
    """
    desde: date
    hasta: date
    agrupar: Literal["Dia", "Semana", "Mes", "Anio"]


# ─────────────────────────
# CONFIGURACIÓN DE KPIs
# ─────────────────────────

class KPIsConfig(BaseModel):
    importe: bool = True
    piezas: bool = True
    devoluciones: bool = True


# ─────────────────────────
# RESUMEN GENERAL KPIs
# ─────────────────────────

class ResumenKPIs(BaseModel):
    importe_total: float = 0.0
    piezas_total: int = 0
    devoluciones_total: int = 0


# ─────────────────────────
# KPI POR PERSONA (tooltip)
# ─────────────────────────

class PersonaKPI(BaseModel):
    id: Optional[str]
    nombre: str
    kpis: Dict[str, float | int]


# ─────────────────────────
# PUNTO DE SERIE TEMPORAL
# ─────────────────────────

class PuntoSerie(BaseModel):
    """
    Un punto del eje temporal (día / semana / mes / año)
    """
    key: str
    label: str
    kpis: Dict[str, float | int]
    personas: List[PersonaKPI]


# ─────────────────────────
# SERIE TEMPORAL RICA
# ─────────────────────────

class SerieTemporal(BaseModel):
    """
    Serie temporal con personas por punto.
    """
    periodo: Literal["dia", "semana", "mes", "anio"]
    serie: List[PuntoSerie]


# ─────────────────────────
# RESPUESTA FINAL DE REPORTES
# ─────────────────────────

class ReporteOut(BaseModel):
    # KPIs activos
    kpis: KPIsConfig

    # Resumen global
    resumen: ResumenKPIs

    # Serie principal (gráfica)
    general: Optional[SerieTemporal] = None

    # Otras vistas (tablas / breakdowns)
    por_zona: Dict[str, Any] = {}
    por_pasillo: Dict[str, Any] = {}
    por_persona: Dict[str, Any] = {}

    # Tabla detalle
    tabla: List[Dict[str, Any]] = []

    # Error opcional
    error: Optional[str] = None
