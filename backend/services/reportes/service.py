import pandas as pd

from backend.db.mongo.reportes.filtros import (rango_fechas,combinar_filtros,)

# ─── DATA ─────────────────────────────────────────────
from backend.services.reportes.data.queries import (cargar_devoluciones_detalle,)
from backend.services.reportes.data.dataframe import (obtener_dataframe,)

# ─── NORMALIZATION ────────────────────────────────────
from backend.services.reportes.normalization import (normalizar_ids, normalizar_columnas, normalizar_tipos,)

# ─── AGGREGATIONS ─────────────────────────────────────
from backend.services.reportes.aggregations import (agrupa_general, agrupa_por_zona, agrupa_por_pasillo, tabla_final)

# ─── PERSONAS ─────────────────────────────────────────
from backend.services.reportes.personas import (agrupar_por_persona,)

# ─── TEMPORAL ─────────────────────────────────────────
from backend.services.reportes.temporal import (map_periodo,normalizar_por_dia,normalizar_por_semana,normalizar_por_mes,normalizar_por_anio,)


class ReportesService:
    """
    Servicio central de reportes (solo lectura).

    RESPONSABILIDAD:
    - Orquestar queries, normalización, agregaciones y series temporales
    - Construir el payload final para el frontend

    NO:
    - Acceso directo a Mongo
    - Lógica de negocio
    - UI
    """

    def __init__(self, reportes_queries):
        self.reportes_queries = reportes_queries

    # ─────────────────────────────
    # API PÚBLICA
    # ─────────────────────────────
    def generar(self, desde, hasta, agrupar="Mes", kpis=None):

        # ─────────────────────────
        # KPIs
        # ─────────────────────────
        kpis = self._normalizar_kpis(kpis)

        # ─────────────────────────
        # Fechas
        # ─────────────────────────
        desde, hasta = self._normalizar_fechas(desde, hasta)
        if desde > hasta:
            return self._resultado_error(
                kpis,
                "La fecha 'desde' no puede ser mayor que 'hasta'"
            )

        # ─────────────────────────
        # Filtros Mongo
        # ─────────────────────────
        filtros = combinar_filtros(
            rango_fechas(desde, hasta)
        )

        # ─────────────────────────
        # Query base
        # ─────────────────────────
        raw = cargar_devoluciones_detalle(
            self.reportes_queries,
            filtros
        )

        df = obtener_dataframe(raw)

        if df is None or df.empty:
            return self._resultado_vacio(kpis)

        # ─────────────────────────
        # Normalización DataFrame
        # ─────────────────────────
        df = normalizar_ids(df)
        df = normalizar_columnas(df, kpis)
        df = normalizar_tipos(df)

        if "fecha" not in df.columns:
            raise ValueError("El DataFrame debe contener la columna 'fecha'")

        # ─────────────────────────
        # KPIs globales
        # ─────────────────────────
        resumen = {
            "importe_total": float(df["importe"].sum()) if kpis["importe"] else 0,
            "piezas_total": int(df["piezas"].sum()) if kpis["piezas"] else 0,
            "devoluciones_total": int(df["devoluciones"].sum()) if kpis["devoluciones"] else 0,
        }

        # ─────────────────────────
        # Agrupaciones
        # ─────────────────────────
        por_persona = agrupar_por_persona(
            self.reportes_queries,
            df,
            desde,
            hasta,
            kpis,
        )

        por_zona = agrupa_por_zona(df, kpis)
        por_pasillo = agrupa_por_pasillo(df, kpis)

        # ─────────────────────────
        # Serie GENERAL (fecha real)
        # ─────────────────────────
        raw_general = agrupa_general(df, kpis)

        periodo = map_periodo(agrupar)

        if periodo == "dia":
            general = normalizar_por_dia(raw_general, desde, hasta)
        elif periodo == "semana":
            general = normalizar_por_semana(raw_general, desde, hasta)
        elif periodo == "anio":
            general = normalizar_por_anio(raw_general, desde, hasta)
        else:
            general = normalizar_por_mes(raw_general, desde, hasta)

        # ─────────────────────────
        # Resultado final
        # ─────────────────────────
        return {
            "kpis": kpis,
            "resumen": resumen,
            "general": general,
            "por_zona": por_zona,
            "por_pasillo": por_pasillo,
            "por_persona": por_persona,
            "tabla": tabla_final(df),
        }

    # ─────────────────────────────
    # HELPERS
    # ─────────────────────────────
    def _normalizar_kpis(self, kpis):
        if kpis is None:
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
        d = pd.to_datetime(desde, errors="coerce").date()
        h = pd.to_datetime(hasta, errors="coerce").date()
        return d, h

    def _resultado_vacio(self, kpis):
        return {
            "kpis": kpis,
            "resumen": {
                "importe_total": 0,
                "piezas_total": 0,
                "devoluciones_total": 0,
            },
            "general": None,
            "por_zona": {},
            "por_pasillo": {},
            "por_persona": {},
            "tabla": [],
        }

    def _resultado_error(self, kpis, mensaje):
        return {
            "kpis": kpis,
            "error": mensaje,
            "resumen": {
                "importe_total": 0,
                "piezas_total": 0,
                "devoluciones_total": 0,
            },
            "general": None,
            "por_zona": {},
            "por_pasillo": {},
            "por_persona": {},
            "tabla": [],
        }
