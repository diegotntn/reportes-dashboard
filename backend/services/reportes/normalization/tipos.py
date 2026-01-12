import pandas as pd


def normalizar_tipos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza tipos de datos del DataFrame.

    - Numéricos: importe, piezas, devoluciones
    - Texto: zona, pasillo, persona
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    # ───── numéricos ─────
    if "importe" in df.columns:
        df["importe"] = pd.to_numeric(
            df["importe"], errors="coerce"
        ).fillna(0.0)

    for col in ("piezas", "devoluciones"):
        if col in df.columns:
            df[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(0)
                .astype(int)
            )

    # ───── texto ─────
    for col in ("zona", "pasillo", "persona"):
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df
