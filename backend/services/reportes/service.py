import pandas as pd

from backend.db.mongo.reportes.filtros import (
    rango_fechas,
    combinar_filtros,
)

# ─── DATA ─────────────────────────────────────────────
from backend.services.reportes.data.queries import (
    cargar_devoluciones_detalle,
)

from backend.services.reportes.data.dataframe import (
    obtener_dataframe,
)

# ─── NORMALIZATION ────────────────────────────────────
from backend.services.reportes.normalization import (
    normalizar_ids,
    normalizar_columnas,
    normalizar_tipos,
)

# ─── AGGREGATIONS ─────────────────────────────────────
from backend.services.reportes.aggregations import (
    agrupa_por_zona,
    agrupa_por_pasillo,
    tabla_final,
)

# ─── GENERAL ──────────────────────────────────────────
from backend.services.reportes.aggregations.general import (
    agrupa_general,
)

# ─── PERSONAS ─────────────────────────────────────────
from backend.services.reportes.personas import (
    agrupar_por_persona,          # TABLA / RESUMEN
)

from backend.services.reportes.personas.agrupacion import (
    agrupar_personas_por_fecha,   # 📈 SERIES
)

# ─── TEMPORAL ─────────────────────────────────────────
from backend.services.reportes.temporal import (
    map_periodo,
    serie_por_dia,
    serie_por_semana,
    serie_por_mes,
    serie_por_anio,
)


class ReportesService:
    """
    Servicio central de reportes (solo lectura).

    RESPONSABILIDAD:
    - Orquestar queries
    - Normalizar datos
    - Construir agregaciones
    - Preparar payload FINAL para frontend
    """

    def __init__(self, reportes_queries):
        self.reportes_queries = reportes_queries

    # ─────────────────────────────
    # API PÚBLICA
    # ─────────────────────────────
    def generar(self, desde, hasta, agrupar="Mes", kpis=None):

        # ─── KPIs
        kpis = self._normalizar_kpis(kpis)

        # ─── Fechas
        desde, hasta = self._normalizar_fechas(desde, hasta)
        if not desde or not hasta or desde > hasta:
            return self._resultado_error(kpis, "Rango de fechas inválido")

        # ─── Filtros Mongo
        filtros = combinar_filtros(
            rango_fechas(desde, hasta)
        )

        # ─── Query base
        raw = cargar_devoluciones_detalle(
            self.reportes_queries,
            filtros
        )

        if raw is None or raw.empty:
            return self._resultado_vacio(kpis, desde, hasta, agrupar)

        # ─── Dimensiones (LECTURA PURA)
        asignaciones = self.reportes_queries.asignaciones_personal()
        personas_map = self.reportes_queries.personas_activas()

        # ─── DataFrame enriquecido
        df = obtener_dataframe(
            raw,
            asignaciones=asignaciones,
            personas_map=personas_map,
        )

        if df is None or df.empty:
            return self._resultado_vacio(kpis, desde, hasta, agrupar)

        # ─── Normalización
        df = normalizar_ids(df)
        df = normalizar_columnas(df, kpis)
        df = normalizar_tipos(df)

        df["devoluciones"] = df.get("devoluciones", 1)
        df["persona_nombre"] = (
            df.get("persona_nombre", "Sin asignación")
              .fillna("Sin asignación")
        )

        # ─── KPIs globales
        resumen = {
            "importe_total": float(df["importe"].sum()) if kpis.get("importe") else 0.0,
            "piezas_total": int(df["piezas"].sum()) if kpis.get("piezas") else 0,
            "devoluciones_total": int(df["devoluciones"].sum()) if kpis.get("devoluciones") else 0,
        }

        # ─── GENERAL (serie temporal)
        periodo = map_periodo(agrupar)

        if periodo == "dia":
            general = serie_por_dia(df, desde, hasta)
        elif periodo == "semana":
            general = serie_por_semana(df, desde, hasta)
        elif periodo == "anio":
            general = serie_por_anio(df, desde, hasta)
        else:
            general = serie_por_mes(df, desde, hasta)

        # ─── PERSONAS
        por_persona = agrupar_por_persona(
            self.reportes_queries,
            df,
            desde,
            hasta,
            kpis,
        )

        personas_series = agrupar_personas_por_fecha(
            df,
            kpis
        )

        # ─── OTRAS DIMENSIONES
        por_zona = agrupa_por_zona(df, kpis)
        por_pasillo = agrupa_por_pasillo(df, kpis)

        # ─── RESULTADO FINAL (CONTRATO FRONTEND)
        return {
            "kpis": kpis,
            "resumen": resumen,

            "general": {
                "periodo": periodo,
                "serie": general,
            },

            "por_zona": por_zona,
            "por_pasillo": por_pasillo,

            # 🔑 PERSONAS (CLAVE PARA UI)
            "personas": personas_map,          # 👈 MAPA id → nombre
            "por_persona": por_persona,        # tablas / resumen
            "personas_series": personas_series,

            "tabla": tabla_final(df),
        }

    # ─────────────────────────────
    # HELPERS
    # ─────────────────────────────
    def _normalizar_kpis(self, kpis):
        if not kpis:
            return {
                "importe": True,
                "piezas": True,
                "devoluciones": True,
            }
        return {
            "importe": bool(kpis.get("importe", True)),
            "piezas": bool(kpis.get("piezas", True)),
            "devoluciones": bool(kpis.get("devoluciones", True)),
        }

    def _normalizar_fechas(self, desde, hasta):
        d = pd.to_datetime(desde, errors="coerce")
        h = pd.to_datetime(hasta, errors="coerce")
        if pd.isna(d) or pd.isna(h):
            return None, None
        return d.date(), h.date()

    def _resultado_vacio(self, kpis, desde, hasta, agrupar):
        return {
            "kpis": kpis,
            "resumen": {
                "importe_total": 0.0,
                "piezas_total": 0,
                "devoluciones_total": 0,
            },
            "general": {
                "periodo": map_periodo(agrupar),
                "serie": [],
            },
            "por_zona": {},
            "por_pasillo": {},
            "personas": {},
            "por_persona": {},
            "personas_series": {},
            "tabla": [],
        }

    def _resultado_error(self, kpis, mensaje):
        return {
            "kpis": kpis,
            "error": mensaje,
            "general": None,
            "por_zona": {},
            "por_pasillo": {},
            "personas": {},
            "por_persona": {},
            "personas_series": {},
            "tabla": [],
        }
