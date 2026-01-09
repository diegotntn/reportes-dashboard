import time
import pandas as pd
import numpy as np

from .queries import obtener_dataframe
from .periodo import map_periodo
from .aggregations import (
    agrupa_general,
    agrupa_por_zona,
    agrupa_por_pasillo,
    tabla_final,
)
from backend.db.mongo.reportes.filtros import (
    rango_fechas,
    combinar_filtros,
)

from backend.services.reportes.normalizadores import (
    normalizar_por_dia,
    normalizar_por_semana,
    normalizar_por_mes,
    normalizar_por_anio,
)



class ReportesService:
    """
    Servicio central de reportes.

    PERSONAS = Personal asignado a pasillos (NO vendedores)

    Responsabilidad:
    - Orquestar queries + agregaciones
    - Normalizar datos para el frontend
    - Construir respuesta final (kpis, resumen, agrupaciones, tabla)

    NO:
    - Acceso directo a Mongo
    - UI
    """

    def __init__(self, reportes_queries, personal_service):
        """
        reportes_queries: ReportesQueries
        personal_service: PersonalService
        """
        self.reportes_queries = reportes_queries
        self.personal_service = personal_service
        self._ultimo_resultado = None
        
    def _to_python(self, obj):
        """
        Convierte tipos numpy / pandas a tipos nativos Python.
        """
        if isinstance(obj, dict):
            return {k: self._to_python(v) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self._to_python(v) for v in obj]

        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        return obj

    # ─────────────────────────────
    # API PÚBLICA
    # ─────────────────────────────
    def _generar(self, desde, hasta, agrupar="Mes", kpis=None):

        # ─────────────────────────
        # KPIs
        # ─────────────────────────
        kpis = self._normalizar_kpis(kpis)

        # ─────────────────────────
        # Validar fechas
        # ─────────────────────────
        desde, hasta = self._normalizar_fechas(desde, hasta)
        if desde > hasta:
            return self._resultado_error(
                kpis=kpis,
                mensaje="La fecha 'desde' no puede ser mayor que 'hasta'."
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
        df_raw = self.reportes_queries.devoluciones_detalle(filtros)
        df = obtener_dataframe(df_raw)

        if df is None or df.empty:
            return self._resultado_vacio(kpis)

        # ─────────────────────────
        # Normalización DataFrame
        # ─────────────────────────
        df = self._normalizar_ids(df)
        df = self._normalizar_columnas(df, kpis)
        df = self._normalizar_tipos(df)

        if "fecha" not in df.columns:
            raise ValueError("El DataFrame debe contener la columna 'fecha'")

        # ─────────────────────────
        # KPIs globales
        # ─────────────────────────
        resumen = {
            "importe_total": float(df["importe"].sum()) if kpis.get("importe") else 0,
            "piezas_total": int(df["piezas"].sum()) if kpis.get("piezas") else 0,
            "devoluciones_total": int(df["devoluciones"].sum()) if kpis.get("devoluciones") else 0,
        }

        # ─────────────────────────
        # Agrupación por persona
        # ─────────────────────────
        por_persona = self._agrupar_por_persona(
            df=df,
            desde=desde,
            hasta=hasta,
            kpis=kpis
        )

        # ─────────────────────────
        # Serie GENERAL RAW (por fecha real)
        # ─────────────────────────
        raw_general = agrupa_general(df, kpis)

        # ─────────────────────────
        # Normalización temporal (ZOOM REAL)
        # ─────────────────────────
        agrupar = (agrupar or "mes").lower()

        if agrupar == "dia":
            general = normalizar_por_dia(raw_general, desde, hasta)

        elif agrupar == "semana":
            general = normalizar_por_semana(raw_general, desde, hasta)

        elif agrupar == "mes":
            general = normalizar_por_mes(raw_general, desde, hasta)

        elif agrupar == "anio":
            general = normalizar_por_anio(raw_general, desde, hasta)

        else:
            general = {"labels": [], "series": {}}

        # 🔍 Debug útil (puedes quitarlo luego)
        print("🟥 AGRUPAR:", agrupar)
        print("🟩 PUNTOS GENERAL:", len(general["labels"]))

        # ─────────────────────────
        # Resultado final
        # ─────────────────────────
        resultado = {
            "kpis": kpis,
            "resumen": resumen,
            "general": general,
            "por_zona": agrupa_por_zona(df, kpis),
            "por_pasillo": agrupa_por_pasillo(df, kpis),
            "por_persona": por_persona,
            "tabla": tabla_final(df),
        }

        self._ultimo_resultado = resultado
        return resultado
  
    # PERSONAS (pasillo → persona)
    # ─────────────────────────────
    def _agrupar_por_persona(self, df, desde, hasta, kpis):
        asignaciones = self.personal_service.obtener_asignaciones_activas(
            desde=desde,
            hasta=hasta
        )

        if not asignaciones:
            return {}

        # normalizar claves por si vienen raras
        pasillo_a_persona = {}
        for a in asignaciones:
            pas = (a.get("pasillo") or "").strip()
            per = (a.get("persona") or "").strip()
            if pas and per:
                pasillo_a_persona[pas] = per

        if not pasillo_a_persona:
            return {}

        # acumulado por indices
        acumulado = {}
        for idx, row in df.iterrows():
            pasillo = row.get("pasillo")
            if pd.isna(pasillo):
                continue
            pasillo = str(pasillo).strip()
            persona = pasillo_a_persona.get(pasillo)

            if not persona:
                continue

            acumulado.setdefault(persona, []).append(idx)

        if not acumulado:
            return {}

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

            # ⚠️ si no quieres mandar df al frontend, cámbialo por tabla_final(df_p)
            resultado[persona] = {
                "df": df_p,
                "resumen": resumen,
            }

        return resultado

    # ─────────────────────────────
    # NORMALIZACIONES
    # ─────────────────────────────
    def _normalizar_kpis(self, kpis):
        if kpis is None:
            return {
                "importe": True,
                "piezas": True,
                "devoluciones": True,
            }

        # asegurar llaves mínimas
        return {
            "importe": bool(kpis.get("importe", True)),
            "piezas": bool(kpis.get("piezas", True)),
            "devoluciones": bool(kpis.get("devoluciones", True)),
        }

    def _normalizar_fechas(self, desde, hasta):
        # Acepta date, datetime o string YYYY-MM-DD
        d = pd.to_datetime(desde, errors="coerce").date()
        h = pd.to_datetime(hasta, errors="coerce").date()

        # si falla conversión, deja algo seguro para que no truene
        if pd.isna(pd.Timestamp(d)) or d is None:
            d = pd.Timestamp.today().date()
        if pd.isna(pd.Timestamp(h)) or h is None:
            h = pd.Timestamp.today().date()

        return d, h

    def _normalizar_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "_id" in df.columns and "id" not in df.columns:
            df["id"] = df["_id"].astype(str)
        return df

    def _normalizar_columnas(self, df: pd.DataFrame, kpis: dict) -> pd.DataFrame:
        df = df.copy()

        # piezas
        if "piezas" not in df.columns:
            if "cantidad" in df.columns:
                df["piezas"] = df["cantidad"]
            else:
                df["piezas"] = 0

        # devoluciones
        if "devoluciones" not in df.columns:
            df["devoluciones"] = 0

        # importe
        if kpis.get("importe"):
            if "importe" in df.columns:
                pass
            elif "total" in df.columns:
                df["importe"] = df["total"]
            elif "subtotal" in df.columns:
                df["importe"] = df["subtotal"]
            else:
                df["importe"] = 0.0
        else:
            if "importe" not in df.columns:
                df["importe"] = 0.0

        # columnas esperadas para cruces
        for col in ("zona", "pasillo"):
            if col not in df.columns:
                df[col] = ""

        return df

    def _normalizar_tipos(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # numericos
        for col in ("importe",):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        for col in ("piezas", "devoluciones"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        # strings
        for col in ("zona", "pasillo"):
            if col in df.columns:
                df[col] = df[col].fillna("").astype(str).str.strip()

        return df

    # ─────────────────────────────
    # RESPUESTAS
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

    def _resultado_error(self, kpis, mensaje: str):
        # Si quieres, el frontend puede mostrarlo en un banner
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
    
    
