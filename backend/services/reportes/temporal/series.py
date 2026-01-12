from datetime import date
import pandas as pd


# ======================================================
# Helpers internos
# ======================================================

def _punto_vacio(key: str, label: str) -> dict:
    return {
        "key": key,
        "label": label,
        "kpis": {
            "importe": 0,
            "piezas": 0,
            "devoluciones": 0,
        },
        "personas": []
    }


def _construir_punto(key: str, label: str, bloque: pd.DataFrame) -> dict:
    personas = []

    for pid, p in bloque.groupby("persona_id", dropna=False):
        personas.append({
            "id": pid,
            "nombre": p["persona_nombre"].iloc[0],
            "kpis": {
                "importe": float(p["importe"].sum()),
                "piezas": int(p["piezas"].sum()),
                "devoluciones": int(p["devoluciones"].sum()),
            }
        })

    return {
        "key": key,
        "label": label,
        "kpis": {
            "importe": float(bloque["importe"].sum()),
            "piezas": int(bloque["piezas"].sum()),
            "devoluciones": int(bloque["devoluciones"].sum()),
        },
        "personas": personas
    }


# ======================================================
# SERIE POR DÍA
# ======================================================

def serie_por_dia(df: pd.DataFrame, desde: date, hasta: date) -> list[dict]:
    if df is None or df.empty:
        return []

    df = df.copy()
    df["dia"] = df["fecha"].dt.date

    salida = []

    for d in pd.date_range(desde, hasta, freq="D").date:
        bloque = df[df["dia"] == d]

        if bloque.empty:
            salida.append(_punto_vacio(str(d), str(d)))
        else:
            salida.append(
                _construir_punto(str(d), str(d), bloque)
            )

    return salida


# ======================================================
# SERIE POR SEMANA (ISO - lunes)
# ======================================================

def serie_por_semana(df: pd.DataFrame, desde: date, hasta: date) -> list[dict]:
    if df is None or df.empty:
        return []

    df = df.copy()
    df["semana"] = (
        df["fecha"] -
        pd.to_timedelta(df["fecha"].dt.weekday, unit="D")
    ).dt.date

    inicio = pd.to_datetime(desde) - pd.to_timedelta(
        pd.to_datetime(desde).weekday(), unit="D"
    )
    fin = pd.to_datetime(hasta) + pd.to_timedelta(
        6 - pd.to_datetime(hasta).weekday(), unit="D"
    )

    salida = []

    for s in pd.date_range(inicio, fin, freq="W-MON").date:
        bloque = df[df["semana"] == s]

        label = f"Semana {s}"

        if bloque.empty:
            salida.append(_punto_vacio(str(s), label))
        else:
            salida.append(
                _construir_punto(str(s), label, bloque)
            )

    return salida


# ======================================================
# SERIE POR MES
# ======================================================

def serie_por_mes(df: pd.DataFrame, desde: date, hasta: date) -> list[dict]:
    if df is None or df.empty:
        return []

    df = df.copy()
    df["mes"] = df["fecha"].dt.to_period("M")

    salida = []

    for m in pd.period_range(desde, hasta, freq="M"):
        bloque = df[df["mes"] == m]

        key = str(m)
        label = str(m)

        if bloque.empty:
            salida.append(_punto_vacio(key, label))
        else:
            salida.append(
                _construir_punto(key, label, bloque)
            )

    return salida


# ======================================================
# SERIE POR AÑO
# ======================================================

def serie_por_anio(df: pd.DataFrame, desde: date, hasta: date) -> list[dict]:
    if df is None or df.empty:
        return []

    df = df.copy()
    df["anio"] = df["fecha"].dt.year

    salida = []

    for a in range(desde.year, hasta.year + 1):
        bloque = df[df["anio"] == a]

        key = str(a)
        label = str(a)

        if bloque.empty:
            salida.append(_punto_vacio(key, label))
        else:
            salida.append(
                _construir_punto(key, label, bloque)
            )

    return salida
