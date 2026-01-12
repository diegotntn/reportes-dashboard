import pandas as pd


def normalizar_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza IDs del DataFrame.

    - Convierte _id de Mongo a string
    - Asegura columna 'id' si existe '_id'
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    if "_id" in df.columns and "id" not in df.columns:
        df["id"] = df["_id"].astype(str)

    return df
