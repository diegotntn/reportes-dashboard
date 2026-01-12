def agrupa_general(df, kpis):
    """
    Agrupación GENERAL por fecha real (datetime).

    RESPONSABILIDAD:
    - Agrupar por fecha
    - Calcular KPIs globales
    - Desglosar KPIs por persona
    - NO formatear fechas (eso es del frontend)

    RETORNA:
    List[dict] compatible con charts.js:
    [
      {
        "fecha": datetime,
        "key": str,
        "label": str,
        "kpis": {...},
        "personas": [
          { "id", "nombre", "kpis": {...} }
        ]
      }
    ]
    """

    # ─────────────────────────────
    # Validaciones base
    # ─────────────────────────────
    if df is None or df.empty:
        return []

    if "fecha" not in df.columns:
        raise ValueError("agrupa_general requiere columna 'fecha'")

    if "persona_id" not in df.columns:
        raise ValueError("agrupa_general requiere columna 'persona_id'")

    # Normalizar columnas KPI presentes
    kpi_cols = []
    if kpis.get("importe") and "importe" in df.columns:
        kpi_cols.append("importe")
    if kpis.get("piezas") and "piezas" in df.columns:
        kpi_cols.append("piezas")
    if kpis.get("devoluciones") and "devoluciones" in df.columns:
        kpi_cols.append("devoluciones")

    if not kpi_cols:
        return []

    resultado = []

    # ─────────────────────────────
    # Agrupar por fecha (GENERAL)
    # ─────────────────────────────
    for fecha, df_fecha in df.groupby("fecha"):

        # ───────── KPIs globales
        kpis_globales = {}
        for c in kpi_cols:
            total = df_fecha[c].sum()
            kpis_globales[c] = float(total) if c == "importe" else int(total)

        # ───────── KPIs por persona
        personas = []

        for persona_id, df_p in df_fecha.groupby("persona_id"):
            if not persona_id:
                continue

            kpis_persona = {}
            for c in kpi_cols:
                val = df_p[c].sum()
                kpis_persona[c] = float(val) if c == "importe" else int(val)

            personas.append({
                "id": persona_id,
                # El nombre real se resuelve después (service / frontend)
                "nombre": df_p.get("persona_nombre", [None])[0],
                "kpis": kpis_persona
            })

        # ───────── Armar punto temporal
        resultado.append({
            "fecha": fecha,                 # datetime (NO string)
            "key": fecha.isoformat(),        # clave estable
            "label": fecha.isoformat(),      # frontend decide formato
            "kpis": kpis_globales,
            "personas": personas
        })

    # Orden cronológico estricto
    resultado.sort(key=lambda x: x["fecha"])

    return resultado
