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
    agrupa_general,
    agrupa_por_zona,
    agrupa_por_pasillo,
    tabla_final,
)

# ─── PERSONAS ─────────────────────────────────────────
from backend.services.reportes.personas import (
    agrupar_por_persona,
)

# ─── TEMPORAL ─────────────────────────────────────────
from backend.services.reportes.temporal import (
    map_periodo,
    # series ricas con personas (NUEVO)
    serie_por_dia,
    serie_por_semana,
    serie_por_mes,
    serie_por_anio,
    # normalización simple (para cards / series simples, si aún la usas en otro lado)
    # normalizar_por_dia,
    # normalizar_por_semana,
    # normalizar_por_mes,
    # normalizar_por_anio,
)


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
        if desde is None or hasta is None:
            return self._resultado_error(kpis, "Fechas inválidas (desde/hasta).")

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
        print("DEBUG filtros Mongo:", filtros)
        self.reportes_queries.debug_find_devoluciones(filtros)
        # ─────────────────────────
        # Query base (eventos)
        # ─────────────────────────
        raw = cargar_devoluciones_detalle(
            self.reportes_queries,
            filtros
        )
        
        print("DEBUG filtros Mongo:", filtros)

        # 🔎 FIND DIRECTO (SIN PIPELINE)

        # ─────────────────────────
        # Debug controlado
        # ─────────────────────────
        if raw is None:
            print("DEBUG raw: None (query no devolvió nada)")
            return self._resultado_vacio(kpis)

        if raw.empty:
            print("DEBUG raw: DataFrame vacío (0 filas)")
            return self._resultado_vacio(kpis)

        print("DEBUG raw filas:", len(raw))
        print("DEBUG raw columnas:", list(raw.columns))
        print("DEBUG raw sample:")
        print(raw.head(3))



        # ─────────────────────────
        # Dimensiones (personas + asignaciones)
        # ─────────────────────────
        # OJO: estos métodos existen en el queries reescrito (db->colecciones)
        asignaciones = self.reportes_queries.asignaciones_personal()

        personas_map = self.reportes_queries.personas_activas()

        # ─────────────────────────
        # DataFrame base + enriquecido con persona
        # ─────────────────────────
        df = obtener_dataframe(
            raw,
            asignaciones=asignaciones,
            personas_map=personas_map,
        )

        if df is None or df.empty:
            return self._resultado_vacio(kpis, desde, hasta, agrupar)

        # ─────────────────────────
        # Normalización DataFrame
        # ─────────────────────────
        df = normalizar_ids(df)
        df = normalizar_columnas(df, kpis)
        df = normalizar_tipos(df)

        if "fecha" not in df.columns:
            raise ValueError("El DataFrame debe contener la columna 'fecha'")

        # Garantiza devoluciones = 1 si no viene
        if "devoluciones" not in df.columns:
            df["devoluciones"] = 1

        # Garantiza persona_nombre
        if "persona_nombre" not in df.columns:
            df["persona_nombre"] = "Sin asignación"
        else:
            df["persona_nombre"] = df["persona_nombre"].fillna("Sin asignación")

        # ─────────────────────────
        # KPIs globales
        # ─────────────────────────
        resumen = {
            "importe_total": float(df["importe"].sum()) if kpis.get("importe") else 0,
            "piezas_total": int(df["piezas"].sum()) if kpis.get("piezas") else 0,
            "devoluciones_total": int(df["devoluciones"].sum()) if kpis.get("devoluciones") else 0,
        }

        # ─────────────────────────
        # Agrupaciones (tablas)
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
        # Serie GENERAL (con personas por punto temporal)
        # ─────────────────────────
        periodo = map_periodo(agrupar)

        if periodo == "dia":
            general = serie_por_dia(df, desde, hasta)
        elif periodo == "semana":
            general = serie_por_semana(df, desde, hasta)
        elif periodo == "anio":
            general = serie_por_anio(df, desde, hasta)
        else:
            general = serie_por_mes(df, desde, hasta)

        # ─────────────────────────
        # Resultado final
        # ─────────────────────────
        return {
            "kpis": kpis,
            "resumen": resumen,
            "general": {
                "periodo": periodo,
                "serie": general
            },
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
        d = pd.to_datetime(desde, errors="coerce")
        h = pd.to_datetime(hasta, errors="coerce")

        if pd.isna(d) or pd.isna(h):
            return None, None

        return d.date(), h.date()

    def _resultado_vacio(self, kpis):
        return {
            "kpis": kpis,
            "resumen": {
                "importe_total": 0.0,
                "piezas_total": 0,
                "devoluciones_total": 0,
            },
            "general": {
                "periodo": None,
                "serie": []
            },
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
