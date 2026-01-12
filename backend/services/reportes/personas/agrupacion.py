import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import date, datetime

from backend.services.reportes.aggregations.tabla import tabla_final


# ─────────────────────────────
# Utilidades
# ─────────────────────────────
def normalizar_fecha(valor) -> Optional[date]:
    """
    Convierte valores de fecha provenientes de Mongo a `datetime.date`.

    Acepta:
    - None
    - datetime.date
    - datetime.datetime
    - str ISO (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)

    Retorna:
    - date o None
    """
    if valor is None:
        return None

    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, str):
        try:
            return datetime.fromisoformat(valor).date()
        except ValueError:
            return None

    return None


# ─────────────────────────────
# Agrupación principal
# ─────────────────────────────
def agrupar_por_persona(
    reportes_queries,
    df: pd.DataFrame,
    desde: date,
    hasta: date,
    kpis: Dict[str, bool],
) -> Dict[str, Any]:
    """
    Agrupa devoluciones por persona usando asignaciones históricas.

    RESPONSABILIDAD:
    - Cruza devoluciones (DataFrame ya normalizado)
    - Aplica lógica temporal de asignaciones activas
    - Calcula KPIs y genera tablas finales

    REGLAS:
    - NO consulta Mongo directamente
    - NO construye pipelines
    - Queries SOLO proveen datos crudos
    """

    # ─────────────────────────────
    # Validaciones base
    # ─────────────────────────────
    if df is None or df.empty:
        return {}

    if not kpis:
        return {}

    if not isinstance(desde, date) or not isinstance(hasta, date):
        raise ValueError("`desde` y `hasta` deben ser datetime.date")

    # ─────────────────────────────
    # Obtener asignaciones CRUDAS
    # ─────────────────────────────
    asignaciones: List[Dict] = reportes_queries.asignaciones_personal()

    if not asignaciones:
        return {}

    # ─────────────────────────────
    # Filtrar asignaciones activas
    # (lógica temporal VIVE AQUÍ)
    # ─────────────────────────────
    asignaciones_activas: List[Dict[str, str]] = []

    for a in asignaciones:
        pasillo = (a.get("pasillo") or "").strip()
        persona_id = (a.get("persona_id") or "").strip()

        if not pasillo or not persona_id:
            continue

        fecha_desde = normalizar_fecha(a.get("fecha_desde"))
        fecha_hasta = normalizar_fecha(a.get("fecha_hasta"))

        # Si empieza después del rango, no aplica
        if fecha_desde and fecha_desde > hasta:
            continue

        # Si terminó antes del rango, no aplica
        if fecha_hasta and fecha_hasta < desde:
            continue

        asignaciones_activas.append({
            "pasillo": pasillo,
            "persona_id": persona_id,
        })

    if not asignaciones_activas:
        return {}

    # ─────────────────────────────
    # Mapa pasillo → persona
    # ─────────────────────────────
    pasillo_a_persona: Dict[str, str] = {
        a["pasillo"]: a["persona_id"]
        for a in asignaciones_activas
    }

    # ─────────────────────────────
    # Agrupar índices por persona
    # ─────────────────────────────
    indices_por_persona: Dict[str, List[int]] = {}

    for idx, row in df.iterrows():
        pasillo = str(row.get("pasillo", "")).strip()
        persona_id = pasillo_a_persona.get(pasillo)

        if not persona_id:
            continue

        indices_por_persona.setdefault(persona_id, []).append(idx)

    if not indices_por_persona:
        return {}

    # ─────────────────────────────
    # Construir resultado final
    # ─────────────────────────────
    resultado: Dict[str, Any] = {}

    for persona_id, idxs in indices_por_persona.items():
        df_persona = df.loc[idxs]

        resumen: Dict[str, Any] = {}

        if kpis.get("importe") and "importe" in df_persona:
            resumen["importe"] = float(df_persona["importe"].sum())

        if kpis.get("piezas") and "piezas" in df_persona:
            resumen["piezas"] = int(df_persona["piezas"].sum())

        if kpis.get("devoluciones") and "devoluciones" in df_persona:
            resumen["devoluciones"] = int(df_persona["devoluciones"].sum())

        resultado[persona_id] = {
            "resumen": resumen,
            "tabla": tabla_final(df_persona),
        }

    return resultado
