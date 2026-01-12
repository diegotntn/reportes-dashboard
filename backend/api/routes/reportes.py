"""
Rutas API para reportes.

RESPONSABILIDAD:
- Recibir parámetros HTTP
- Validar entrada mínima
- Delegar a ReportesService.generar()
- Devolver JSON serializado

NO CONTIENE:
- Lógica de negocio
- Acceso a Mongo
- Pandas / numpy como dependencia lógica
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, date
from decimal import Decimal

from backend.api.dependencies import get_reportes_service
from backend.api.schemas.reportes import ReportesFiltros
from backend.services.reportes.service import ReportesService


router = APIRouter(tags=["Reportes"])


# ─────────────────────────────
# SERIALIZADOR SEGURO
# ─────────────────────────────
def _serialize_data(data):
    if isinstance(data, dict):
        return {k: _serialize_data(v) for k, v in data.items()}

    if isinstance(data, list):
        return [_serialize_data(v) for v in data]

    if isinstance(data, (datetime, date)):
        return data.isoformat()

    if isinstance(data, Decimal):
        return float(data)

    return data


# ─────────────────────────────
# ENDPOINT
# ─────────────────────────────
@router.post("", summary="Generar reportes")
def generar_reportes(
    filtros: ReportesFiltros,
    service: ReportesService = Depends(get_reportes_service),
):
    """
    Body esperado:
    {
        "desde": "YYYY-MM-DD",
        "hasta": "YYYY-MM-DD",
        "agrupar": "Dia | Semana | Mes | Anio"
    }
    """

    # ─────────────────────────
    # Validación mínima
    # ─────────────────────────
    if filtros.desde > filtros.hasta:
        raise HTTPException(
            status_code=400,
            detail="La fecha 'desde' no puede ser mayor que 'hasta'",
        )

    # ─────────────────────────
    # Delegar a Service
    # ─────────────────────────
    resultado = service.generar(
        desde=filtros.desde,
        hasta=filtros.hasta,
        agrupar=filtros.agrupar,
        kpis=filtros.kpis if hasattr(filtros, "kpis") else None,
    )

    # ─────────────────────────
    # Respuesta serializada
    # ─────────────────────────
    return JSONResponse(
        content=_serialize_data(resultado)
    )
