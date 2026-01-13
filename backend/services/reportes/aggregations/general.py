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

    # ─────────────────────────────
    # Determinar KPIs válidos
    # ─────────────────────────────
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
    # Agrupación GENERAL por fecha
    # ─────────────────────────────
    for fecha, df_fecha in df.groupby("fecha", dropna=False):

        # ───────── KPIs globales
        kpis_globales = {}
        for col in kpi_cols:
            total = df_fecha[col].sum()
            kpis_globales[col] = (
                float(total) if col == "importe" else int(total)
            )

        # ───────── KPIs por persona
        personas = []

        for persona_id, df_persona in df_fecha.groupby("persona_id", dropna=False):

            # Normalizar ID
            persona_id_norm = persona_id if persona_id else "SIN_ASIGNACION"

            # Resolver nombre de forma segura
            nombre = None
            if "persona_nombre" in df_persona.columns:
                val = df_persona["persona_nombre"].iloc[0]
                if val and str(val).strip():
                    nombre = str(val)

            if not nombre:
                nombre = "Sin asignación"

            # KPIs por persona
            kpis_persona = {}
            for col in kpi_cols:
                total = df_persona[col].sum()
                kpis_persona[col] = (
                    float(total) if col == "importe" else int(total)
                )

            personas.append({
                "id": persona_id_norm,
                "nombre": nombre,
                "kpis": kpis_persona
            })

        # ───────── Punto temporal final
        resultado.append({
            "fecha": fecha,                  # datetime real
            "key": fecha.isoformat(),         # clave estable
            "label": fecha.isoformat(),       # frontend decide formato
            "kpis": kpis_globales,
            "personas": personas
        })

    # ─────────────────────────────
    # Orden cronológico estricto
    # ─────────────────────────────
    resultado.sort(key=lambda x: x["fecha"])

    return resultado
