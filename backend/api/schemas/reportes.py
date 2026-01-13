from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Literal
from datetime import date


# ─────────────────────────────
# FILTROS DE ENTRADA
# ─────────────────────────────

class ReportesFiltros(BaseModel):
    """
    Filtros enviados desde el frontend.
    """
    desde: date
    hasta: date
    agrupar: Literal["Dia", "Semana", "Mes", "Anio"]


# ─────────────────────────────
# CONFIGURACIÓN DE KPIs
# ─────────────────────────────

class KPIsConfig(BaseModel):
    importe: bool = True
    piezas: bool = True
    devoluciones: bool = True


# ─────────────────────────────
# RESUMEN GLOBAL
# ─────────────────────────────

class ResumenKPIs(BaseModel):
    importe_total: float = 0.0
    piezas_total: int = 0
    devoluciones_total: int = 0


# ─────────────────────────────
# KPIs POR PERSONA (tooltip / breakdown)
# ─────────────────────────────

class PersonaKPI(BaseModel):
    id: Optional[str]
    nombre: str
    kpis: Dict[str, float | int]


# ─────────────────────────────
# PUNTO TEMPORAL (SERIE RICA)
# ─────────────────────────────

class PuntoSerie(BaseModel):
    """
    Un punto del eje temporal (día / semana / mes / año)
    """
    key: str
    label: str
    kpis: Dict[str, float | int]
    personas: List[PersonaKPI] = []


# ─────────────────────────────
# SERIE TEMPORAL
# ─────────────────────────────

class SerieTemporal(BaseModel):
    """
    Serie temporal rica con personas por punto.
    """
    periodo: Literal["dia", "semana", "mes", "anio"]
    serie: List[PuntoSerie]


# ─────────────────────────────
# TABLA POR PERSONA
# ─────────────────────────────

class PersonaTabla(BaseModel):
    """
    Tabla + resumen por persona (vista personas)
    """
    resumen: Dict[str, float | int]
    tabla: List[Dict[str, Any]]


# ─────────────────────────────
# SERIES POR PERSONA (NUEVO)
# ─────────────────────────────

class PersonaSerie(BaseModel):
    """
    Serie temporal individual por persona
    """
    persona_id: str
    nombre: str
    periodo: Literal["dia", "semana", "mes", "anio"]
    serie: List[PuntoSerie]


# ─────────────────────────────
# RESPUESTA FINAL DE REPORTES
# ─────────────────────────────

class ReporteOut(BaseModel):
    # KPIs activos
    kpis: KPIsConfig

    # Resumen global
    resumen: ResumenKPIs

    # Serie principal (GENERAL)
    general: Optional[SerieTemporal] = None

    # Breakdown clásicos
    por_zona: Dict[str, Any] = {}
    por_pasillo: Dict[str, Any] = {}

    # Personas (TABLA)
    por_persona: Dict[str, PersonaTabla] = {}

    # Personas (SERIES PARA GRÁFICAS)
    personas_series: Dict[str, PersonaSerie] = {}

    # Tabla detalle
    tabla: List[Dict[str, Any]] = []

    # Error opcional
    error: Optional[str] = None
