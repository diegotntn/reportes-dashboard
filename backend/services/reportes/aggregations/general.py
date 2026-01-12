def agrupa_general(df, kpis):
    """
    Agrupación general BASE por fecha real.

    RETORNA:
    List[dict] con fecha como datetime (NO string)
    """
    if df is None or df.empty:
        return []

    if "fecha" not in df.columns:
        raise ValueError("agrupa_general requiere columna 'fecha'")

    agg = {}

    if kpis.get("importe"):
        agg["importe"] = ("importe", "sum")

    if kpis.get("piezas"):
        agg["piezas"] = ("piezas", "sum")

    if kpis.get("devoluciones"):
        agg["devoluciones"] = ("devoluciones", "sum")

    if not agg:
        return []

    df_agg = (
        df.groupby("fecha", as_index=False)
        .agg(**agg)
        .sort_values("fecha")
    )

    # ⚠️ NO convertir fecha a string aquí
    # df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

    for c in ("importe",):
        if c in df_agg.columns:
            df_agg[c] = df_agg[c].astype(float)

    for c in ("piezas", "devoluciones"):
        if c in df_agg.columns:
            df_agg[c] = df_agg[c].astype(int)

    return df_agg.to_dict(orient="records")