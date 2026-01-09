import pandas as pd


def obtener_dataframe(df_detalle):
    """
    Normaliza el DataFrame base para reportes.

    Entrada:
    - DataFrame YA obtenido desde Mongo (aggregate)
    - Debe incluir:
        - periodo
        - zona
        - pasillo (opcional)
        - piezas
        - importe
        - devoluciones

    Salida:
    - DataFrame listo para aggregations.py
    """
    if df_detalle is None or df_detalle.empty:
        return None

    df = df_detalle.copy()

    # Normalización mínima
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"])

    # Si el pipeline no trae devoluciones explícitas
    if "devoluciones" not in df.columns:
        df["devoluciones"] = 1

    return df
