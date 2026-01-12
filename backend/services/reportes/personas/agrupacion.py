import pandas as pd
from backend.services.reportes.aggregations.tabla import tabla_final


def agrupar_por_persona(
    reportes_queries,
    df: pd.DataFrame,
    desde,
    hasta,
    kpis: dict,
):
    """
    Agrupa devoluciones por persona usando asignaciones históricas.

    REGLAS:
    - NO consulta Mongo directamente
    - Usa reportes_queries para obtener asignaciones
    - El DataFrame ya viene normalizado
    """

    if df is None or df.empty:
        return {}

    # ─────────────────────────
    # Obtener asignaciones activas
    # ─────────────────────────
    asignaciones = reportes_queries.asignaciones_activas(
        desde=desde,
        hasta=hasta
    )

    if not asignaciones:
        return {}

    # ─────────────────────────
    # Mapa pasillo → persona
    # ─────────────────────────
    pasillo_a_persona = {}
    for a in asignaciones:
        pasillo = (a.get("pasillo") or "").strip()
        persona = (a.get("persona") or "").strip()

        if pasillo and persona:
            pasillo_a_persona[pasillo] = persona

    if not pasillo_a_persona:
        return {}

    # ─────────────────────────
    # Agrupar índices por persona
    # ─────────────────────────
    acumulado = {}

    for idx, row in df.iterrows():
        pasillo = str(row.get("pasillo", "")).strip()
        persona = pasillo_a_persona.get(pasillo)

        if not persona:
            continue

        acumulado.setdefault(persona, []).append(idx)

    if not acumulado:
        return {}

    # ─────────────────────────
    # Construir resultado final
    # ─────────────────────────
    resultado = {}

    for persona, idxs in acumulado.items():
        df_p = df.loc[idxs]

        resumen = {}

        if kpis.get("importe"):
            resumen["importe"] = float(df_p["importe"].sum())

        if kpis.get("piezas"):
            resumen["piezas"] = int(df_p["piezas"].sum())

        if kpis.get("devoluciones"):
            resumen["devoluciones"] = int(df_p["devoluciones"].sum())

        resultado[persona] = {
            "resumen": resumen,
            "tabla": tabla_final(df_p),
        }

    return resultado
