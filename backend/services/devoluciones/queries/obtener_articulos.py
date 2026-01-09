"""
Query: obtener artículos de una devolución.

RESPONSABILIDAD:
- Obtener artículos para el panel derecho del historial
- Normalizar el contrato de columnas para la UI

NO HACE:
- Validaciones de negocio
- Acceso directo a Mongo
"""

import pandas as pd

# Contrato de columnas que la UI espera
_UI_COLUMNS = ["id", "nombre", "codigo", "pasillo", "cantidad", "unitario"]


def obtener_articulos(reportes_queries, devolucion_id: str) -> pd.DataFrame:
    """
    Devuelve los artículos de una devolución como DataFrame.

    Parámetros:
    - reportes_queries: instancia de ReportesQueries
    - devolucion_id: id de la devolución

    Garantías:
    - Nunca devuelve None
    - Siempre incluye la columna 'id'
    """

    # ─────────────────────────────────────────────
    # Validación mínima de entrada
    # ─────────────────────────────────────────────
    if not devolucion_id:
        return pd.DataFrame(columns=_UI_COLUMNS)

    # ─────────────────────────────────────────────
    # Lectura especializada (Mongo aggregation)
    # ─────────────────────────────────────────────
    df = reportes_queries.devolucion_articulos(devolucion_id)

    if df is None or df.empty:
        return pd.DataFrame(columns=_UI_COLUMNS)

    # ─────────────────────────────────────────────
    # Normalización de ID (contrato UI)
    # ─────────────────────────────────────────────
    if "id" not in df.columns:
        if "_id" in df.columns:
            df = df.rename(columns={"_id": "id"})
        elif "producto_id" in df.columns:
            df = df.rename(columns={"producto_id": "id"})
        else:
            # Generar id sintético para no romper la UI
            df = df.copy()
            df["id"] = df.index.astype(str)

    # ─────────────────────────────────────────────
    # Garantizar columnas mínimas (orden y presencia)
    # ─────────────────────────────────────────────
    for col in _UI_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df = df[_UI_COLUMNS]

    return df
