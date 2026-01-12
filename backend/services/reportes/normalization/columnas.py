import pandas as pd


def normalizar_columnas(df: pd.DataFrame, kpis: dict) -> pd.DataFrame:
    """
    Asegura columnas mínimas requeridas para reportes.

    Columnas garantizadas:
    - fecha
    - importe
    - piezas
    - devoluciones
    - zona
    - pasillo
    - persona (opcional)
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # ───── piezas ─────
    if "piezas" not in df.columns:
        if "cantidad" in df.columns:
            df["piezas"] = df["cantidad"]
        else:
            df["piezas"] = 0

    # ───── devoluciones ─────
    if "devoluciones" not in df.columns:
        df["devoluciones"] = 1

    # ───── importe ─────
    if kpis.get("importe", True):
        if "importe" in df.columns:
            pass
        elif "total" in df.columns:
            df["importe"] = df["total"]
        elif "subtotal" in df.columns:
            df["importe"] = df["subtotal"]
        else:
            df["importe"] = 0.0
    else:
        df["importe"] = 0.0

    # ───── dimensiones ─────
    for col in ("zona", "pasillo", "persona"):
        if col not in df.columns:
            df[col] = ""

    return df
