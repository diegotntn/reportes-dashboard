"""
Normalizadores de series temporales para reportes.

RESPONSABILIDAD:
- Recibir datos agregados crudos (por fecha real)
- Construir ejes temporales COMPLETOS y calendarizados
- Rellenar valores faltantes con 0
- Entregar estructura lista para Chart.js
"""

from datetime import date
import pandas as pd
from calendar import month_name


# ======================================================
# Utilidades internas
# ======================================================

def _to_dataframe(raw: list[dict]) -> pd.DataFrame:
    if not raw:
        return pd.DataFrame()

    df = pd.DataFrame(raw)

    if "fecha" not in df.columns:
        raise ValueError("Se requiere columna 'fecha'")

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])

    return df


def _metricas(df):
    return [c for c in df.columns if c != "fecha"]


def _empty(labels, metricas):
    return {
        "labels": labels,
        "series": {m: [0] * len(labels) for m in metricas}
    }


# ======================================================
# NORMALIZACIÓN POR DÍA (REAL)
# ======================================================

def normalizar_por_dia(raw, desde: date, hasta: date):
    df = _to_dataframe(raw)

    dias = pd.date_range(desde, hasta, freq="D")
    labels = dias.strftime("%Y-%m-%d").tolist()

    if df.empty:
        return _empty(labels, [])

    metricas = _metricas(df)

    df = (
        df.set_index("fecha")
        .reindex(dias, fill_value=0)
        .reset_index(drop=True)
    )

    return {
        "labels": labels,
        "series": {m: df[m].tolist() for m in metricas}
    }


# ======================================================
# NORMALIZACIÓN POR SEMANA (REAL, lunes–domingo)
# ======================================================

def normalizar_por_semana(raw, desde: date, hasta: date):
    df = _to_dataframe(raw)

    # Ajustar rango a semanas completas
    inicio = pd.to_datetime(desde) - pd.to_timedelta(pd.to_datetime(desde).weekday(), unit="D")
    fin = pd.to_datetime(hasta) + pd.to_timedelta(6 - pd.to_datetime(hasta).weekday(), unit="D")

    semanas = pd.date_range(inicio, fin, freq="W-MON")

    labels = [f"Semana del {s.strftime('%Y-%m-%d')}" for s in semanas]

    if df.empty:
        return _empty(labels, [])

    metricas = _metricas(df)

    # Representar cada fecha por el lunes de su semana
    df["_semana"] = df["fecha"] - pd.to_timedelta(df["fecha"].dt.weekday, unit="D")

    agrupado = (
        df.groupby("_semana")[metricas]
        .sum()
        .reindex(semanas, fill_value=0)
    )

    return {
        "labels": labels,
        "series": {m: agrupado[m].tolist() for m in metricas}
    }


# ======================================================
# NORMALIZACIÓN POR MES (REAL)
# ======================================================

def normalizar_por_mes(raw, desde: date, hasta: date):
    df = _to_dataframe(raw)

    meses = pd.period_range(desde, hasta, freq="M")
    labels = [month_name[p.month] for p in meses]

    if df.empty:
        return _empty(labels, [])

    metricas = _metricas(df)

    df["_mes"] = df["fecha"].dt.to_period("M")

    agrupado = (
        df.groupby("_mes")[metricas]
        .sum()
        .reindex(meses, fill_value=0)
    )

    return {
        "labels": labels,
        "series": {m: agrupado[m].tolist() for m in metricas}
    }


# ======================================================
# NORMALIZACIÓN POR AÑO (REAL)
# ======================================================

def normalizar_por_anio(raw, desde: date, hasta: date):
    df = _to_dataframe(raw)

    anios = list(range(desde.year, hasta.year + 1))
    labels = [str(a) for a in anios]

    if df.empty:
        return _empty(labels, [])

    metricas = _metricas(df)

    df["_anio"] = df["fecha"].dt.year

    agrupado = (
        df.groupby("_anio")[metricas]
        .sum()
        .reindex(anios, fill_value=0)
    )

    return {
        "labels": labels,
        "series": {m: agrupado[m].tolist() for m in metricas}
    }
