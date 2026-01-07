import pandas as pd
from utils.helpers import money

def exportar_excel(resultado, path):
    df = pd.DataFrame(resultado["tabla"])
    df["importe"] = df["importe"].map(money)
    df.to_excel(path, index=False)
