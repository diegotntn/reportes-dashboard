def agrupa_por_pasillo(df, kpis):
    """
    Agrupación por pasillo.

    - Excluye registros sin pasillo válido
    - Normaliza valores inválidos ('—', None, '')
    - Devuelve claves semánticas consistentes para el frontend
    """
    if df is None or df.empty or "pasillo" not in df.columns:
        return {}

    # ─────────────────────────
    # Normalización de pasillo
    # ─────────────────────────
    df = df.copy()

    df["pasillo"] = (
        df["pasillo"]
        .astype(str)
        .str.strip()
        .replace({
            "nan": None,
            "None": None,
            "—": None,
            "-": None,
            "": None,
        })
    )

    # Eliminar filas sin pasillo válido
    df = df[df["pasillo"].notna()]

    if df.empty:
        return {}

    resultado = {}

    # ─────────────────────────
    # Agrupación por pasillo
    # ─────────────────────────
    for pasillo, g in df.groupby("pasillo"):

        resumen = {}

        if kpis.get("importe"):
            resumen["importe"] = float(g["importe"].sum())

        if kpis.get("piezas"):
            resumen["piezas"] = int(g["piezas"].sum())

        if kpis.get("devoluciones"):
            resumen["devoluciones"] = int(g["devoluciones"].sum())

        # Definición de agregaciones por fecha
        agg = {}

        if kpis.get("importe"):
            agg["importe"] = ("importe", "sum")

        if kpis.get("piezas"):
            agg["piezas"] = ("piezas", "sum")

        if kpis.get("devoluciones"):
            agg["devoluciones"] = ("devoluciones", "sum")

        if not agg:
            continue

        df_agg = (
            g.groupby("fecha", as_index=False)
            .agg(**agg)
            .sort_values("fecha")
        )

        # Normalizar fecha a string ISO
        df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

        resultado[str(pasillo)] = {
            "series": df_agg.to_dict(orient="records"),
            "resumen": resumen,
        }

    return resultado
