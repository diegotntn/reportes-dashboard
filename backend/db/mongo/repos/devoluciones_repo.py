from datetime import datetime
from typing import Any, Iterable

import pandas as pd


class DevolucionesRepo:
    """
    Repositorio MongoDB para la colección `devoluciones`.

    RESPONSABILIDAD:
    - Acceso directo a MongoDB (colección)
    - CRUD de devoluciones
    - Ejecución de pipelines de agregación
    - Conversión básica a estructuras de apoyo (DataFrame)

    NO HACE:
    - Lógica de negocio
    """

    def __init__(self, db):
        """
        Parámetros
        ----------
        db : pymongo.database.Database
            Base de datos Mongo.
        """
        self.collection = db["devoluciones"]

    # ───────────────────────── Helpers ─────────────────────────

    @staticmethod
    def _to_datetime(value: Any) -> datetime:
        """
        Asegura un objeto datetime válido para MongoDB.
        """
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    @staticmethod
    def _to_df(docs: Iterable[dict]) -> pd.DataFrame:
        """
        Convierte una lista de documentos Mongo a DataFrame.
        """
        return pd.DataFrame(list(docs)) if docs else pd.DataFrame()

    # ───────────────────────── CRUD ─────────────────────────

    def insertar(
        self,
        *,
        devolucion_id: str,
        fecha,
        folio: str,
        cliente: str,
        direccion: str,
        motivo: str,
        zona: str,
        total: float,
        articulos: list[dict],
        vendedor_id: str | None = None,
        estatus: str = "pendiente",
    ) -> None:
        """
        Inserta una nueva devolución.
        """
        doc = {
            "_id": devolucion_id,
            "fecha": self._to_datetime(fecha),
            "folio": folio,
            "cliente": cliente,
            "direccion": direccion,
            "motivo": motivo,
            "zona": zona,
            "total": float(total),
            "articulos": articulos or [],
            "vendedor_id": vendedor_id,
            "estatus": estatus,
            "created_at": datetime.utcnow(),
        }

        self.collection.insert_one(doc)

    def actualizar(self, devolucion_id: str, *, data: dict) -> None:
        """
        Actualiza campos específicos de una devolución.
        """
        if not data:
            return

        self.collection.update_one(
            {"_id": devolucion_id},
            {"$set": data},
        )

    def eliminar(self, devolucion_id: str) -> None:
        """
        Elimina una devolución por ID.
        """
        self.collection.delete_one({"_id": devolucion_id})

    def eliminar_todas(self) -> None:
        """
        Elimina todas las devoluciones.
        (Uso exclusivo para tests).
        """
        self.collection.delete_many({})

    # ───────────────────────── Queries simples ─────────────────────────

    def listar(self, filtros: dict) -> pd.DataFrame:
        """
        Lista devoluciones aplicando filtros simples.
        """
        docs = list(
            self.collection.find(filtros).sort(
                [("fecha", -1), ("folio", -1)]
            )
        )

        for d in docs:
            d["id"] = d.pop("_id")

            if isinstance(d.get("fecha"), datetime):
                d["fecha"] = d["fecha"].date().isoformat()

        return self._to_df(docs)

    def articulos(self, devolucion_id: str) -> pd.DataFrame:
        """
        Devuelve los artículos de una devolución (consulta simple).
        """
        doc = self.collection.find_one({"_id": devolucion_id})
        if not doc:
            return pd.DataFrame()

        rows = []
        for idx, art in enumerate(doc.get("articulos", [])):
            r = dict(art)
            r["id"] = str(idx)
            rows.append(r)

        return self._to_df(rows)

    # ───────────────────────── Aggregations ─────────────────────────

    def aggregate(self, pipeline: list[dict]) -> list[dict]:
        """
        Ejecuta un pipeline de agregación MongoDB.

        Usado exclusivamente por ReportesQueries.
        """
        return list(self.collection.aggregate(pipeline))
