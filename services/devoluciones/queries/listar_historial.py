"""
Query: listar historial de devoluciones.

RESPONSABILIDAD:
- Construir filtro Mongo válido
- Normalizar fechas a datetime
- Delegar ejecución a DB
- Retornar DataFrame listo para UI
"""

import pandas as pd
from datetime import datetime, date


# ─────────────────────────────────────────────
# Helpers locales (solo para este query)
# ─────────────────────────────────────────────

def _dt_inicio(value):
    """Convierte date | datetime | str a datetime (inicio del día)."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(str(value))


def _dt_fin(value):
    """Convierte date | datetime | str a datetime (fin del día)."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.max.time())
    return datetime.fromisoformat(str(value))


# ─────────────────────────────────────────────
# Query principal
# ─────────────────────────────────────────────

def listar_historial(db, *, desde=None, hasta=None, **otros_filtros) -> pd.DataFrame:
    """
    Devuelve el historial de devoluciones como DataFrame.
    """

    # ───── Filtro Mongo único ─────
    filtro = {}

    # Filtro por fecha
    if desde or hasta:
        filtro["fecha"] = {}

        if desde:
            filtro["fecha"]["$gte"] = _dt_inicio(desde)
        if hasta:
            filtro["fecha"]["$lte"] = _dt_fin(hasta)

    # Otros filtros simples (zona, estatus, vendedor_id, etc.)
    for k, v in otros_filtros.items():
        if v is not None:
            filtro[k] = v

    # ───── Ejecución DB ─────
    data = db.get_devoluciones(filtro=filtro)

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)
