from pymongo import MongoClient
from datetime import datetime
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

    # ─────────────────────────────
    # 🔹 INIT
    # ─────────────────────────────
    def __init__(self, uri: str, db_name: str):
        print("\n🔌 [MongoClientProvider] Conectando a MongoDB...")
        print("   URI:", uri)
        print("   DB :", db_name)

        self._client = MongoClient(uri)
        self._db = self._client[db_name]

        print("✅ [MongoClientProvider] Conexión creada")
        print("📦 [MongoClientProvider] Colecciones disponibles:")
        try:
            for c in self._db.list_collection_names():
                print("   -", c)
        except Exception as e:
            print("❌ Error listando colecciones:", e)

    # ─────────────────────────────
    # 🔹 ACCESO GENÉRICO
    # ─────────────────────────────
    def get_collection(self, name: str):
        """
        Devuelve una colección Mongo (uso interno por services / queries).
        """
        print(f"\n📁 [MongoClientProvider] get_collection('{name}')")

        if name not in self._db.list_collection_names():
            print(f"⚠️  Colección '{name}' NO existe en la base")

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
        """

        print("\n🧪 [MongoClientProvider] find_devoluciones")

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

        print("➡️  Query final:", query)

        try:
            total_docs = self._db.devoluciones.count_documents({})
            match_docs = self._db.devoluciones.count_documents(query)

            print("📦 Total devoluciones:", total_docs)
            print("🎯 Coinciden con query:", match_docs)

            sample = list(self._db.devoluciones.find(query).limit(1))
            if sample:
                print("📄 Sample documento:")
                print(sample[0])
                print("📅 Tipo de fecha:", type(sample[0].get("fecha")))
            else:
                print("⚠️  Query no devolvió documentos")

            return list(self._db.devoluciones.find(query))

        except Exception as e:
            print("❌ ERROR en find_devoluciones:", e)
            return []

    # ─────────────────────────────
    # 🔹 AGGREGATE DEVOLUCIONES
    # ─────────────────────────────
    def aggregate_devoluciones(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Ejecuta un aggregate sobre la colección devoluciones.
        """

        print("\n🧪 [MongoClientProvider] aggregate_devoluciones")
        print("📐 Pipeline recibido:")
        for i, stage in enumerate(pipeline):
            print(f"   {i+1}. {stage}")

        try:
            result = list(self._db.devoluciones.aggregate(pipeline))

            print("🎯 Resultado aggregate:", len(result))

            if result:
                print("📄 Sample aggregate:")
                print(result[0])
            else:
                print("⚠️  Aggregate devolvió 0 filas")

            return result

        except Exception as e:
            print("❌ ERROR en aggregate_devoluciones:", e)
            return []

    # ─────────────────────────────
    # 🔹 DEVOLUCIÓN COMPLETA
    # ─────────────────────────────
    def get_devolucion_completa(self, devolucion_id) -> Dict | None:
        print("\n🔍 [MongoClientProvider] get_devolucion_completa")
        print("   ID:", devolucion_id)

        try:
            doc = self._db.devoluciones.find_one({"_id": devolucion_id})
            print("   Encontrado:", bool(doc))
            return doc
        except Exception as e:
            print("❌ ERROR get_devolucion_completa:", e)
            return None

    # ─────────────────────────────
    # 🔹 PERSONAL (LECTURA)
    # ─────────────────────────────
    def listar_personal(self, solo_activos: bool = True) -> List[Dict]:
        print("\n👥 [MongoClientProvider] listar_personal")
        query = {"activo": True} if solo_activos else {}
        print("➡️  Query:", query)
        return list(self._db.personal.find(query))

    # ─────────────────────────────
    # 🔹 ASIGNACIONES (LECTURA)
    # ─────────────────────────────
    def listar_asignaciones(self) -> List[Dict]:
        print("\n📋 [MongoClientProvider] listar_asignaciones")
        return list(self._db.asignaciones.find())

    # ─────────────────────────────
    # 🔹 VENDEDORES (LECTURA)
    # ─────────────────────────────
    def listar_vendedores(self, solo_activos: bool = True) -> List[Dict]:
        print("\n🧑‍💼 [MongoClientProvider] listar_vendedores")
        query = {"activo": True} if solo_activos else {}
        print("➡️  Query:", query)
        return list(self._db.vendedores.find(query))

    # ─────────────────────────────
    # 🔹 LIFECYCLE
    # ─────────────────────────────
    def close(self):
        print("\n🔌 [MongoClientProvider] Cerrando conexión MongoDB")
        self._client.close()
