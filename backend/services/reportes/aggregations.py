"""
Funciones de agregación para reportes.

REGLAS:
- NO consultan DB
- NO conocen la UI
- SOLO trabajan con el DataFrame normalizado

Contrato del DataFrame de entrada:
- fecha (datetime)
- importe (float)
- piezas (int)
- devoluciones (int)
- zona (str, opcional)
- pasillo (str, opcional)
- persona (str, opcional)
"""

import pandas as pd


# ─────────────────────────────
def agrupa_general(df, kpis):
    """
    Agrupación general BASE por fecha real.

    RETORNA:
    List[dict] con fecha como datetime (NO string)
    """
    if df is None or df.empty:
        return []

    if "fecha" not in df.columns:
        raise ValueError("agrupa_general requiere columna 'fecha'")

    agg = {}

    if kpis.get("importe"):
        agg["importe"] = ("importe", "sum")

    if kpis.get("piezas"):
        agg["piezas"] = ("piezas", "sum")

    if kpis.get("devoluciones"):
        agg["devoluciones"] = ("devoluciones", "sum")

    if not agg:
        return []

    df_agg = (
        df.groupby("fecha", as_index=False)
        .agg(**agg)
        .sort_values("fecha")
    )

    # ⚠️ NO convertir fecha a string aquí
    # df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

    for c in ("importe",):
        if c in df_agg.columns:
            df_agg[c] = df_agg[c].astype(float)

    for c in ("piezas", "devoluciones"):
        if c in df_agg.columns:
            df_agg[c] = df_agg[c].astype(int)

    return df_agg.to_dict(orient="records")

# ─────────────────────────────
def agrupa_por_zona(df, kpis):
    """
    Agrupación por zona.

    RETORNA:
    {
        "Z11": {
            "series": [...],
            "resumen": {...}
        }
    }
    """
    if df is None or df.empty or "zona" not in df.columns:
        return {}

    resultado = {}

    for zona, g in df.groupby("zona"):
        if not zona:
            continue

        resumen = {}
        if kpis.get("importe"):
            resumen["importe"] = float(g["importe"].sum())
        if kpis.get("piezas"):
            resumen["piezas"] = int(g["piezas"].sum())
        if kpis.get("devoluciones"):
            resumen["devoluciones"] = int(g["devoluciones"].sum())

        agg = {}
        if kpis.get("importe"):
            agg["importe"] = ("importe", "sum")
        if kpis.get("piezas"):
            agg["piezas"] = ("piezas", "sum")
        if kpis.get("devoluciones"):
            agg["devoluciones"] = ("devoluciones", "sum")

        if not agg:
            continue

        df_agg = (
            g.groupby("fecha", as_index=False)
            .agg(**agg)
            .sort_values("fecha")
        )

        df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

        resultado[zona] = {
            "series": df_agg.to_dict(orient="records"),
            "resumen": resumen,
        }

    return resultado


# ─────────────────────────────
def agrupa_por_pasillo(df, kpis):
    """
    Agrupación por pasillo.
    """
    if df is None or df.empty or "pasillo" not in df.columns:
        return {}

    resultado = {}

    for pasillo, g in df.groupby("pasillo"):
        if not pasillo:
            continue

        resumen = {}
        if kpis.get("importe"):
            resumen["importe"] = float(g["importe"].sum())
        if kpis.get("piezas"):
            resumen["piezas"] = int(g["piezas"].sum())
        if kpis.get("devoluciones"):
            resumen["devoluciones"] = int(g["devoluciones"].sum())

        agg = {}
        if kpis.get("importe"):
            agg["importe"] = ("importe", "sum")
        if kpis.get("piezas"):
            agg["piezas"] = ("piezas", "sum")
        if kpis.get("devoluciones"):
            agg["devoluciones"] = ("devoluciones", "sum")

        if not agg:
            continue

        df_agg = (
            g.groupby("fecha", as_index=False)
            .agg(**agg)
            .sort_values("fecha")
        )

        df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

        resultado[pasillo] = {
            "series": df_agg.to_dict(orient="records"),
            "resumen": resumen,
        }

    return resultado


# ─────────────────────────────
def tabla_final(df):
    """
    Tabla de detalle final.

    RESPONSABILIDAD:
    - Mostrar totales por fecha + dimensiones disponibles
    - NO depende de 'periodo'
    - NO calendariza
    """
    if df is None or df.empty:
        return []

    if "fecha" not in df.columns:
        raise ValueError("tabla_final requiere columna 'fecha'")

    group_cols = ["fecha"]

    if "zona" in df.columns:
        group_cols.append("zona")

    if "pasillo" in df.columns:
        group_cols.append("pasillo")

    if "persona" in df.columns:
        group_cols.append("persona")

    grp = (
        df.groupby(group_cols, as_index=False)
        .agg(
            devoluciones=("devoluciones", "sum"),
            piezas=("piezas", "sum"),
            importe=("importe", "sum"),
        )
        .sort_values(group_cols)
    )

    grp["fecha"] = grp["fecha"].dt.strftime("%Y-%m-%d")

    salida = []
    for _, r in grp.iterrows():
        row = {
            "fecha": r["fecha"],
            "devoluciones": int(r["devoluciones"]),
            "piezas": int(r["piezas"]),
            "importe": float(r["importe"]),
        }

        if "zona" in grp.columns:
            row["zona"] = r.get("zona")

        if "pasillo" in grp.columns:
            row["pasillo"] = r.get("pasillo")

        if "persona" in grp.columns:
            row["persona"] = r.get("persona")

        salida.append(row)

    return salida
