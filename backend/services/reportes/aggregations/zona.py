def agrupa_por_zona(df, kpis):
    """
    Agrupación por zona.

    RETORNA:
    {
        "Z11": {
            "series": [...],
            "resumen": {...}
        }
    }
    """
    if df is None or df.empty or "zona" not in df.columns:
        return {}

    resultado = {}

    for zona, g in df.groupby("zona"):
        if not zona:
            continue

        resumen = {}
        if kpis.get("importe"):
            resumen["importe"] = float(g["importe"].sum())
        if kpis.get("piezas"):
            resumen["piezas"] = int(g["piezas"].sum())
        if kpis.get("devoluciones"):
            resumen["devoluciones"] = int(g["devoluciones"].sum())

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

        df_agg["fecha"] = df_agg["fecha"].dt.strftime("%Y-%m-%d")

        resultado[zona] = {
            "series": df_agg.to_dict(orient="records"),
            "resumen": resumen,
        }

    return resultado

