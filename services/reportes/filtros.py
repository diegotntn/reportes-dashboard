def aplicar_filtros(df, zona, pasillo, motivos):
    if zona != "Todas":
        df = df[df["zona"] == zona]

    if pasillo != "Todos":
        df = df[df["pasillo"] == pasillo]

    if motivos:
        df = df[df["motivo"].isin(motivos)]

    return df
