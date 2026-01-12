import pandas as pd
from typing import Dict, List

from .pipelines import (
    pipeline_devoluciones_detalle,
    pipeline_devoluciones_resumen,
    pipeline_devolucion_articulos,
)


class ReportesQueries:
    """
    Ejecuta consultas especializadas para REPORTES.

    RESPONSABILIDAD:
    - Construir pipelines Mongo
    - Ejecutar aggregate / find sobre colecciones reales
    - Devolver datos CRUDOS (DataFrame o list)

    NO HACE:
    - Lógica de negocio
    - Inferencias temporales
    - Agrupaciones analíticas finales
    """

    # ─────────────────────────────
    # INIT
    # ─────────────────────────────
    def __init__(self, provider):
        """
        provider: MongoClientProvider
        """
        print("\n🧩 [ReportesQueries] inicializando...")

        self.provider = provider

        # 🔑 Colecciones REALES (PyMongo Collection)
        self.devoluciones = provider.get_collection("devoluciones")
        self.personas = provider.get_collection("personal")
        self.asignaciones = provider.get_collection("asignaciones")

        print("   ✔ Colecciones conectadas:")
        print("     - devoluciones :", self.devoluciones.full_name)
        print("     - personas     :", self.personas.full_name)
        print("     - asignaciones :", self.asignaciones.full_name)

    # ─────────────────────────────
    # DEVOLUCIONES (BASE ANALÍTICA)
    # ─────────────────────────────
    def devoluciones_detalle(self, filtros: Dict) -> pd.DataFrame:
        """
        Devuelve eventos base de devoluciones
        (UNA FILA POR ARTÍCULO).
        """
        print("\n📊 [ReportesQueries] devoluciones_detalle()")
        print("➡ Filtros:", filtros)

        pipeline = pipeline_devoluciones_detalle(filtros)
        print("🧩 Pipeline etapas:", len(pipeline))

        data = list(self.devoluciones.aggregate(pipeline))
        print("📦 Filas devueltas por aggregate:", len(data))

        if not data:
            print("⚠️ devoluciones_detalle: SIN RESULTADOS")
            return pd.DataFrame(
                columns=[
                    "fecha",
                    "zona",
                    "pasillo",
                    "piezas",
                    "importe",
                    "devoluciones",
                ]
            )

        df = pd.DataFrame(data)
        print("✅ devoluciones_detalle DataFrame creado:", df.shape)
        return df

    # ─────────────────────────────
    # RESUMEN ADMINISTRATIVO
    # ─────────────────────────────
    def devoluciones_resumen(self, filtros: Dict) -> pd.DataFrame:
        """
        Devuelve resumen administrativo
        (UNA FILA POR DEVOLUCIÓN).
        """
        print("\n📋 [ReportesQueries] devoluciones_resumen()")
        print("➡ Filtros:", filtros)

        pipeline = pipeline_devoluciones_resumen(filtros)

        data = list(self.devoluciones.aggregate(pipeline))
        print("📦 Filas devueltas:", len(data))

        if not data:
            print("⚠️ devoluciones_resumen: SIN RESULTADOS")
            return pd.DataFrame(
                columns=[
                    "id",
                    "fecha",
                    "folio",
                    "cliente",
                    "zona",
                    "estatus",
                    "total",
                ]
            )

        df = pd.DataFrame(data)
        print("✅ devoluciones_resumen DataFrame creado:", df.shape)
        return df

    # ─────────────────────────────
    # ARTÍCULOS POR DEVOLUCIÓN
    # ─────────────────────────────
    def devolucion_articulos(self, devolucion_id: str) -> pd.DataFrame:
        """
        Devuelve artículos de una devolución específica.
        """
        print("\n📦 [ReportesQueries] devolucion_articulos()")
        print("➡ devolucion_id:", devolucion_id)

        pipeline = pipeline_devolucion_articulos(devolucion_id)

        data = list(self.devoluciones.aggregate(pipeline))
        print("📦 Artículos encontrados:", len(data))

        if not data:
            print("⚠️ devolucion_articulos: SIN RESULTADOS")
            return pd.DataFrame(
                columns=[
                    "nombre",
                    "codigo",
                    "pasillo",
                    "cantidad",
                    "unitario",
                ]
            )

        return pd.DataFrame(data)

    # ─────────────────────────────
    # PERSONAS (DIMENSIÓN)
    # ─────────────────────────────
    def personas_activas(self) -> Dict[str, str]:
        """
        Devuelve un MAPA de personas activas.

        RETURN:
        { persona_id: nombre }
        """
        print("\n👥 [ReportesQueries] personas_activas()")

        cursor = self.personas.find(
            {"activo": True},
            {"_id": 1, "nombre": 1}
        )

        personas = {
            str(p["_id"]): p["nombre"]
            for p in cursor
        }

        print("👥 Personas activas encontradas:", len(personas))
        return personas

    # ─────────────────────────────
    # ASIGNACIONES (DIMENSIÓN)
    # ─────────────────────────────
    def asignaciones_personal(self) -> List[Dict]:
        """
        Devuelve TODAS las asignaciones de personal
        (SIN lógica temporal).
        """
        print("\n🧩 [ReportesQueries] asignaciones_personal()")

        cursor = self.asignaciones.find(
            {},
            {
                "_id": 0,
                "pasillo": 1,
                "persona_id": 1,
                "fecha_desde": 1,
                "fecha_hasta": 1,
            }
        )

        data = list(cursor)
        print("🧩 Asignaciones encontradas:", len(data))
        return data

    # ─────────────────────────────
    # DEBUG DIRECTO (SIN PIPELINE)
    # ─────────────────────────────
    def debug_find_devoluciones(self, filtros: Dict):
        """
        DEBUG PURO:
        Acceso directo a Mongo para validar filtros.
        """
        print("\n🔍 [DEBUG] debug_find_devoluciones")
        print("➡ Filtros:", filtros)

        total = self.devoluciones.count_documents(filtros)
        print("📦 Coincidencias:", total)

        docs = list(self.devoluciones.find(filtros).limit(1))

        if docs:
            doc = docs[0]
            print("📄 Sample:", doc)
            print("📅 Tipo fecha:", type(doc.get("fecha")))
        else:
            print("⚠️ Sin documentos")

        return docs

