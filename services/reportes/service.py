import time

from .queries import obtener_dataframe
from .periodo import map_periodo
from .aggregations import (
    agrupa_general,
    agrupa_por_zona,
    agrupa_por_pasillo,
    tabla_final,
)
from db.mongo.reportes.filtros import (
    rango_fechas,
    combinar_filtros,
)


class ReportesService:
    """
    Servicio central de reportes.

    PERSONAS = Personal asignado a pasillos
    (NO vendedores)
    """

    def __init__(self, reportes_queries, personal_service):
        self.reportes_queries = reportes_queries
        self.personal_service = personal_service
        self._ultimo_resultado = None

    # ─────────────────────────────
    # API PÚBLICA
    # ─────────────────────────────
    def generar(self, *, desde, hasta, agrupar="Mes", kpis=None):
        """
        Genera reportes y KPIs según filtros y configuración.
        Mide tiempo de ejecución.
        """
        print("⏳ Generando reporte...")
        t0 = time.time()

        resultado = self._generar(
            desde=desde,
            hasta=hasta,
            agrupar=agrupar,
            kpis=kpis
        )

        print(f"✅ Reporte listo en {time.time() - t0:.2f}s")
        return resultado

    # ─────────────────────────────
    # IMPLEMENTACIÓN REAL
    # ─────────────────────────────
    def _generar(self, desde, hasta, agrupar="Mes", kpis=None):

        if kpis is None:
            kpis = {
                "importe": True,
                "piezas": True,
                "devoluciones": True,
            }

        # ───── Filtros ─────
        filtros = combinar_filtros(
            rango_fechas(desde, hasta)
        )

        # ───── Query base ─────
        df_raw = self.reportes_queries.devoluciones_detalle(filtros)
        df = obtener_dataframe(df_raw)

        if df is None or df.empty:
            return self._resultado_vacio(kpis)

        # ───── Normalizaciones ─────
        df = self._normalizar_ids(df)
        df = self._normalizar_columnas(df, kpis)

        # ───── Periodo ─────
        df["periodo"] = map_periodo(df, agrupar)

        # ───── KPIs globales ─────
        resumen = {
            "importe_total": float(df["importe"].sum()) if kpis.get("importe") else 0,
            "piezas_total": int(df["piezas"].sum()) if kpis.get("piezas") else 0,
            "devoluciones_total": int(df["devoluciones"].sum()) if kpis.get("devoluciones") else 0,
        }

        # ───── Agrupación por persona ─────
        por_persona = self._agrupar_por_persona(
            df=df,
            desde=desde,
            hasta=hasta,
            kpis=kpis
        )

        resultado = {
            "kpis": kpis,
            "resumen": resumen,
            "general": agrupa_general(df, kpis),
            "por_zona": agrupa_por_zona(df, kpis),
            "por_pasillo": agrupa_por_pasillo(df, kpis),
            "por_persona": por_persona,
            "tabla": tabla_final(df),
        }

        self._ultimo_resultado = resultado
        return resultado

    # ─────────────────────────────
    def _agrupar_por_persona(self, df, desde, hasta, kpis):
        asignaciones = self.personal_service.obtener_asignaciones_activas(
            desde=desde,
            hasta=hasta
        )

        if not asignaciones:
            return {}

        pasillo_a_persona = {
            a["pasillo"]: a["persona"]
            for a in asignaciones
        }

        acumulado = {}

        for idx, row in df.iterrows():
            pasillo = row.get("pasillo")
            persona = pasillo_a_persona.get(pasillo)

            if not persona:
                continue

            acumulado.setdefault(persona, []).append(idx)

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
                "df": df_p,
                "resumen": resumen,
            }

        return resultado

    # ─────────────────────────────
    def _normalizar_ids(self, df):
        if "_id" in df.columns and "id" not in df.columns:
            df["id"] = df["_id"].astype(str)
        return df

    # ─────────────────────────────
    def _normalizar_columnas(self, df, kpis):
        df = df.copy()

        if "piezas" not in df.columns:
            df["piezas"] = df.get("cantidad", 0)

        if "devoluciones" not in df.columns:
            df["devoluciones"] = 0

        if kpis.get("importe"):
            if "importe" in df.columns:
                pass
            elif "total" in df.columns:
                df["importe"] = df["total"]
            elif "subtotal" in df.columns:
                df["importe"] = df["subtotal"]
            else:
                df["importe"] = 0.0

        return df

    # ─────────────────────────────
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
