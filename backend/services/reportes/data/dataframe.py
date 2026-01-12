import pandas as pd


def obtener_dataframe(df_detalle):
    """
    Normaliza el DataFrame base para reportes.

    Entrada:
    - DataFrame o lista de dicts proveniente de Mongo
    Salida:
    - DataFrame listo para aggregations
    """
    if df_detalle is None:
        return None

    # Si viene como lista de dicts
    if not isinstance(df_detalle, pd.DataFrame):
        df = pd.DataFrame(df_detalle)
    else:
        df = df_detalle.copy()

    if df.empty:
        return None

    # Normalización mínima
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # Si el pipeline no trae devoluciones explícitas
    if "devoluciones" not in df.columns:
        df["devoluciones"] = 1

    return df
