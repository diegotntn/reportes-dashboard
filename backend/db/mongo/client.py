from pymongo import MongoClient
from datetime import datetime, date
from typing import Any, Dict, List


class MongoClientProvider:
    """
    Proveedor de acceso a MongoDB (SOLO LECTURA).

    RESPONSABILIDADES:
    - Crear y cerrar la conexión
    - Exponer acceso controlado a colecciones
    - Ejecutar consultas find / aggregate
    - NO escribir datos
    - NO contener lógica de negocio
    """

    def __init__(self, uri: str, db_name: str):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]

    # ─────────────────────────────
    # 🔹 ACCESO GENÉRICO
    # ─────────────────────────────
    def get_collection(self, name: str):
        """
        Devuelve una colección Mongo (uso interno por services / queries).
        """
        return self._db[name]

    # ─────────────────────────────
    # 🔹 DEVOLUCIONES (LECTURA)
    # ─────────────────────────────
    def find_devoluciones(
        self,
        *,
        filtro: Dict[str, Any] | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        vendedor_id: str | None = None,
        estatus: str | None = None,
    ) -> List[Dict]:
        """
        Consulta devoluciones mediante Mongo.find().

        CONTRATO:
        - SOLO LECTURA
        - `filtro` Mongo tiene prioridad
        - No transforma tipos
        """

        query: Dict[str, Any] = {}

        if isinstance(filtro, dict):
            query.update(filtro)

        if desde or hasta:
            query["fecha"] = {}
            if desde:
                query["fecha"]["$gte"] = desde
            if hasta:
                query["fecha"]["$lte"] = hasta

        if vendedor_id:
            query["vendedor_id"] = vendedor_id

        if estatus:
            query["estatus"] = estatus

        return list(self._db.devoluciones.find(query))

    def aggregate_devoluciones(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Ejecuta un aggregate sobre la colección devoluciones.

        Usado por servicios de reportes.
        """
        return list(self._db.devoluciones.aggregate(pipeline))

    def get_devolucion_completa(self, devolucion_id) -> Dict | None:
        """
        Devuelve una devolución completa (lectura directa).
        """
        return self._db.devoluciones.find_one({"_id": devolucion_id})

    # ─────────────────────────────
    # 🔹 PERSONAL (LECTURA)
    # ─────────────────────────────
    def listar_personal(self, solo_activos: bool = True) -> List[Dict]:
        query = {}
        if solo_activos:
            query["activo"] = True
        return list(self._db.personal.find(query))

    # ─────────────────────────────
    # 🔹 ASIGNACIONES (LECTURA)
    # ─────────────────────────────
    def listar_asignaciones(self) -> List[Dict]:
        return list(self._db.asignaciones.find())

    # ─────────────────────────────
    # 🔹 VENDEDORES (LECTURA)
    # ─────────────────────────────
    def listar_vendedores(self, solo_activos: bool = True) -> List[Dict]:
        query = {}
        if solo_activos:
            query["activo"] = True
        return list(self._db.vendedores.find(query))

    # ─────────────────────────────
    # 🔹 LIFECYCLE
    # ─────────────────────────────
    def close(self):
        """
        Cierra la conexión MongoDB.
        """
        self._client.close()
