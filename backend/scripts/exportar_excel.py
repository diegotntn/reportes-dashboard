import pandas as pd
from backend.scripts.utils.formato import money


def exportar_excel(resultado: dict, path: str):
    """
    Exporta el resultado de un reporte a Excel.

    resultado: {
        "tabla": [ {col: valor, ...}, ... ]
    }
    """
    df = pd.DataFrame(resultado["tabla"])

    if "importe" in df.columns:
        df["importe"] = df["importe"].map(money)

    df.to_excel(path, index=False)
