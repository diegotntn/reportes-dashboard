import pandas as pd
from datetime import datetime


# ─────────────────────────────
# Helpers internos
# ─────────────────────────────
def _to_date(value):
    """
    Convierte strings o datetime a date comparable.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def _resolver_persona(pasillo, fecha, asignaciones):
    """
    Dado un pasillo y una fecha, devuelve persona_id o None.
    """
    for a in asignaciones:
        if a["pasillo"] != pasillo:
            continue

        desde = _to_date(a.get("fecha_desde"))
        hasta = _to_date(a.get("fecha_hasta"))
        f = _to_date(fecha)

        if desde and hasta and f and desde <= f <= hasta:
            return a.get("persona_id")

    return None


# ─────────────────────────────
# API pública
# ─────────────────────────────
def obtener_dataframe(
    df_detalle,
    asignaciones: list[dict] | None = None,
    personas_map: dict | None = None,
):
    """
    Normaliza y ENRIQUECE el DataFrame base para reportes.
    """

    if df_detalle is None:
        return None

    # Convertir a DataFrame
    df = (
        df_detalle.copy()
        if isinstance(df_detalle, pd.DataFrame)
        else pd.DataFrame(df_detalle)
    )

    if df.empty:
        return None

    # ───────── Normalización mínima
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    if "devoluciones" not in df.columns:
        df["devoluciones"] = 1

    # ───────── Enriquecimiento PERSONA (CLAVE)
    if asignaciones and "pasillo" in df.columns:
        df["persona_id"] = df.apply(
            lambda r: _resolver_persona(
                r.get("pasillo"),
                r.get("fecha"),
                asignaciones
            ),
            axis=1
        )
    else:
        df["persona_id"] = None

    # ───────── Resolver nombre
    if personas_map:
        df["persona_nombre"] = df["persona_id"].map(personas_map)
    else:
        df["persona_nombre"] = None

    # ───────── Fallback explícito
    df["persona_nombre"] = df["persona_nombre"].fillna("Sin asignación")
    
    print(
        "[DEBUG DATAFRAME GENERAL]",
        df[["fecha", "pasillo", "persona_id", "persona_nombre"]]
        .drop_duplicates()
        .head(20)
    )
    
    return df
    
