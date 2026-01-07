import pandas as pd

from .pipelines import (
    pipeline_devoluciones_detalle,
    pipeline_devoluciones_resumen,
    pipeline_devolucion_articulos,
)


class ReportesQueries:
    """
    Ejecuta pipelines de reportes a través del adapter de DB.

    RESPONSABILIDAD:
    - Construir pipelines Mongo
    - Delegar ejecución al adapter DB
    - Convertir resultados a pandas.DataFrame
    - NO contener lógica de negocio
    """

    def __init__(self, db):
        """
        db: BaseDB (MongoClientProvider / SQLiteProvider)
        """
        self.db = db

    # ─────────────────────────────
    def devoluciones_detalle(self, filtros: dict) -> pd.DataFrame:
        """
        Detalle por artículo.
        Base para reportes, KPIs y agrupaciones.
        """
        pipeline = pipeline_devoluciones_detalle(filtros)
        data = self.db.aggregate_devoluciones(pipeline=pipeline)

        return pd.DataFrame(data) if data else pd.DataFrame(
            columns=["fecha", "zona", "pasillo", "piezas", "importe", "devoluciones"]
        )

    # ─────────────────────────────
    def devoluciones_resumen(self, filtros: dict) -> pd.DataFrame:
        """
        Resumen de devoluciones (Historial - tabla izquierda).
        """
        pipeline = pipeline_devoluciones_resumen(filtros)
        data = self.db.aggregate_devoluciones(pipeline=pipeline)

        return pd.DataFrame(data) if data else pd.DataFrame(
            columns=["id", "fecha", "folio", "cliente", "zona", "estatus", "total"]
        )

    # ─────────────────────────────
    def devolucion_articulos(self, devolucion_id: str) -> pd.DataFrame:
        """
        Artículos de una devolución específica (Historial - panel derecho).
        """
        pipeline = pipeline_devolucion_articulos(devolucion_id)
        data = self.db.aggregate_devoluciones(pipeline=pipeline)

        return pd.DataFrame(data) if data else pd.DataFrame(
            columns=["nombre", "codigo", "pasillo", "cantidad", "unitario"]
        )
