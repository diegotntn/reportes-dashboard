def map_periodo(df, modo):
    if modo == "Día":
        return df["fecha"].dt.date.astype(str)
    if modo == "Semana":
        return df["fecha"].dt.to_period("W").astype(str)
    if modo == "Mes":
        return df["fecha"].dt.to_period("M").astype(str)
    if modo == "Año":
        return df["fecha"].dt.year.astype(str)
    raise ValueError("Modo de agrupación inválido")
