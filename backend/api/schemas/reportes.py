from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Literal
from datetime import date


# ─────────────────────────
# FILTROS DE ENTRADA
# ─────────────────────────

class ReportesFiltros(BaseModel):
    """
    Filtros enviados desde el frontend.

    agrupar:
    - Dia
    - Semana
    - Mes
    - Anio
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
# BLOQUES DE REPORTE
# (estructura ya procesada)
# ─────────────────────────

class SerieTemporal(BaseModel):
    labels: List[Any]
    series: Dict[str, List[Any]]
    resumen: Optional[Dict[str, Any]] = None


# ─────────────────────────
# RESPUESTA FINAL DE REPORTES
# ─────────────────────────

class ReporteOut(BaseModel):
    # KPIs activos
    kpis: KPIsConfig

    # Resumen global
    resumen: ResumenKPIs

    # Vistas
    general: Optional[SerieTemporal] = None
    por_zona: Dict[str, SerieTemporal] = {}
    por_pasillo: Dict[str, SerieTemporal] = {}
    por_persona: Dict[str, SerieTemporal] = {}

    # Tabla detalle
    tabla: List[Dict[str, Any]] = []
