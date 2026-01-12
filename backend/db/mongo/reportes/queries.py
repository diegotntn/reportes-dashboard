import pandas as pd

from .pipelines import (
    pipeline_devoluciones_detalle,
    pipeline_devoluciones_resumen,
    pipeline_devolucion_articulos,
)


class ReportesQueries:
    """
    Ejecuta consultas especializadas para reportes.

    RESPONSABILIDAD:
    - Construir pipelines Mongo
    - Ejecutar aggregate sobre la colección
    - Devolver datos en la forma que el servicio necesita

    NO HACE:
    - Lógica de negocio
    - Transformaciones analíticas
    """

    def __init__(self, collection):
        """
        collection: pymongo.collection.Collection
        """
        self.collection = collection
        print("DEBUG collection:", type(self.collection))

    # ─────────────────────────────
    # DEVOLUCIONES (BASE ANALÍTICA)
    # ─────────────────────────────
    def devoluciones_detalle(self, filtros: dict) -> pd.DataFrame:
        pipeline = pipeline_devoluciones_detalle(filtros)
        data = list(self.collection.aggregate(pipeline))

        if not data:
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

        return pd.DataFrame(data)

    # ─────────────────────────────
    def devoluciones_resumen(self, filtros: dict) -> pd.DataFrame:
        pipeline = pipeline_devoluciones_resumen(filtros)
        data = list(self.collection.aggregate(pipeline))

        if not data:
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

        return pd.DataFrame(data)

    # ─────────────────────────────
    def devolucion_articulos(self, devolucion_id: str) -> pd.DataFrame:
        pipeline = pipeline_devolucion_articulos(devolucion_id)
        data = list(self.collection.aggregate(pipeline))

        if not data:
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
    # ASIGNACIONES DE PERSONAL
    # ─────────────────────────────
    def asignaciones_activas(self, **_filtros):
        """
        Devuelve asignaciones activas de personal.

        COMPATIBLE CON:
        - services/reportes/personas/agrupacion.py

        DEVUELVE:
        - List[dict] con:
          { "pasillo": str, "persona": str }
        """

        pipeline = [
            {"$match": {"activo": True}},
            {
                "$project": {
                    "_id": 0,
                    "pasillo": 1,
                    "persona": 1,
                }
            },
        ]

        data = list(self.collection.aggregate(pipeline))

        # 🔑 IMPORTANTE:
        # Devuelve LISTA DE DICTS, no DataFrame
        return data or []
