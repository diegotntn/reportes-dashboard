"""
Query: listar historial de devoluciones.

RESPONSABILIDAD:
- Construir filtros válidos
- Normalizar fechas
- Delegar ejecución al repositorio
- Retornar DataFrame listo para UI / reportes

NO HACE:
- Acceso directo a Mongo
- Lógica de dominio
"""

from datetime import datetime, date
import pandas as pd


# ─────────────────────────────────────────────
# Helpers locales (solo para este query)
# ─────────────────────────────────────────────

def _dt_inicio(value):
    """
    Convierte date | datetime | str a datetime (inicio del día).
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    return datetime.fromisoformat(str(value))


def _dt_fin(value):
    """
    Convierte date | datetime | str a datetime (fin del día).
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.max.time())
    return datetime.fromisoformat(str(value))


# ─────────────────────────────────────────────
# Query principal
# ─────────────────────────────────────────────

def listar_historial(
    *,
    repo,
    desde=None,
    hasta=None,
    **otros_filtros,
) -> pd.DataFrame:
    """
    Devuelve el historial de devoluciones como DataFrame.
    """

    filtros = {}

    # ───── Filtro por fechas ─────
    if desde or hasta:
        filtros["fecha"] = {}

        if desde:
            filtros["fecha"]["$gte"] = _dt_inicio(desde)
        if hasta:
            filtros["fecha"]["$lte"] = _dt_fin(hasta)

    # ───── Otros filtros simples ─────
    for k, v in otros_filtros.items():
        if v is not None:
            filtros[k] = v

    # ───── Delegar ejecución al repositorio ─────
    return repo.listar(filtros)
