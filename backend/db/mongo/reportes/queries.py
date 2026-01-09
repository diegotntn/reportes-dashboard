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
    - Delegar ejecución al repositorio
    - Normalizar resultados para servicios

    NO HACE:
    - Acceso directo a Mongo
    - Lógica de negocio
    """

    def __init__(self, devoluciones_repo):
        """
        devoluciones_repo: DevolucionesRepo
        """
        self.repo = devoluciones_repo
        print("DEBUG repo:", type(self.repo))

    # ─────────────────────────────
    # DEVOLUCIONES (BASE DE REPORTES)
    # ─────────────────────────────
    def devoluciones_detalle(self, filtros: dict) -> pd.DataFrame:
        """
        Detalle por artículo.
        Base para KPIs y agrupaciones.
        """
        pipeline = pipeline_devoluciones_detalle(filtros)
        data = self.repo.aggregate(pipeline)

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
        """
        Resumen general de devoluciones
        (Historial – tabla principal).
        """
        pipeline = pipeline_devoluciones_resumen(filtros)
        data = self.repo.aggregate(pipeline)

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
        """
        Artículos de una devolución específica
        (Historial – panel de detalle).
        """
        pipeline = pipeline_devolucion_articulos(devolucion_id)
        data = self.repo.aggregate(pipeline)

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
