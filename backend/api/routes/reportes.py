"""
Rutas API para reportes.

RESPONSABILIDAD:
- Recibir parámetros HTTP
- Validar entrada mínima
- Delegar a ReportesService._generar()
- Devolver JSON serializado

NO CONTIENE:
- Lógica de negocio
- Acceso a Mongo
- pandas
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
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
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return []
        return data.replace({np.nan: None}).to_dict(orient="records")

    if isinstance(data, pd.Series):
        return data.replace({np.nan: None}).to_dict()

    if isinstance(data, (np.integer, np.floating)):
        return data.item()

    if isinstance(data, np.ndarray):
        return data.tolist()

    if isinstance(data, (datetime, date)):
        return data.isoformat()

    if isinstance(data, Decimal):
        return float(data)

    if isinstance(data, list):
        return [_serialize_data(v) for v in data]

    if isinstance(data, dict):
        return {k: _serialize_data(v) for k, v in data.items()}

    return data


# ─────────────────────────────
# ENDPOINT
# ─────────────────────────────
@router.post("", summary="Generar reportes")
def generar_reportes(
    filtros: ReportesFiltros,
    service: ReportesService = Depends(get_reportes_service)
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
            detail="La fecha 'desde' no puede ser mayor que 'hasta'"
        )

    # 🔎 LOG ÚNICO (como pediste)
    print("🟥 AGRUPAR:", filtros.agrupar.lower())

    # ─────────────────────────
    # Delegar a Service
    # ─────────────────────────
    resultado = service._generar(
        desde=filtros.desde,
        hasta=filtros.hasta,
        agrupar=filtros.agrupar
    )

    # Debug útil
    if resultado.get("general"):
        print("🟩 PUNTOS GENERAL:", len(resultado["general"]["labels"]))

    # ─────────────────────────
    # Serializar salida
    # ─────────────────────────
    return JSONResponse(content=_serialize_data(resultado))
