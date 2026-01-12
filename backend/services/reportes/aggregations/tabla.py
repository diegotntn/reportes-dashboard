def tabla_final(df):
    """
    Tabla de detalle final.

    RESPONSABILIDAD:
    - Mostrar totales por fecha + dimensiones disponibles
    - NO depende de 'periodo'
    - NO calendariza
    """
    if df is None or df.empty:
        return []

    if "fecha" not in df.columns:
        raise ValueError("tabla_final requiere columna 'fecha'")

    group_cols = ["fecha"]

    if "zona" in df.columns:
        group_cols.append("zona")

    if "pasillo" in df.columns:
        group_cols.append("pasillo")

    if "persona" in df.columns:
        group_cols.append("persona")

    grp = (
        df.groupby(group_cols, as_index=False)
        .agg(
            devoluciones=("devoluciones", "sum"),
            piezas=("piezas", "sum"),
            importe=("importe", "sum"),
        )
        .sort_values(group_cols)
    )

    grp["fecha"] = grp["fecha"].dt.strftime("%Y-%m-%d")

    salida = []
    for _, r in grp.iterrows():
        row = {
            "fecha": r["fecha"],
            "devoluciones": int(r["devoluciones"]),
            "piezas": int(r["piezas"]),
            "importe": float(r["importe"]),
        }

        if "zona" in grp.columns:
            row["zona"] = r.get("zona")

        if "pasillo" in grp.columns:
            row["pasillo"] = r.get("pasillo")

        if "persona" in grp.columns:
            row["persona"] = r.get("persona")

        salida.append(row)

    return salida
