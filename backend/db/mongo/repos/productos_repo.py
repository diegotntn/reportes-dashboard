import re
import pandas as pd


class ProductosRepo:
    """
    Repositorio MongoDB para productos.

    RESPONSABILIDADES:
    - Acceso a datos (MongoDB)
    - Consultas de lectura
    - NO contiene lógica de negocio
    - NO conoce API ni UI
    """

    def __init__(self, db):
        """
        Parámetros
        ----------
        db : pymongo.database.Database
            Instancia de la base de datos MongoDB.
        """
        self.col = db.productos

    # ─────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────
    @staticmethod
    def _to_df(docs: list) -> pd.DataFrame:
        """
        Convierte una lista de documentos Mongo en DataFrame.
        """
        return pd.DataFrame(docs) if docs else pd.DataFrame()

    @staticmethod
    def _projection() -> dict:
        """
        Proyección estándar de campos del producto.
        """
        return {
            "_id": 0,
            "clave": 1,
            "nombre": 1,
            "linea": 1,
            "lcd4": 1,
        }

    # ─────────────────────────────────────────
    # LISTADOS
    # ─────────────────────────────────────────
    def listar(self) -> pd.DataFrame:
        """
        Lista todos los productos ordenados por nombre.
        """
        docs = list(
            self.col
            .find({}, self._projection())
            .sort("nombre", 1)
        )
        return self._to_df(docs)

    # ─────────────────────────────────────────
    # OBTENER POR CLAVE EXACTA
    # ─────────────────────────────────────────
    def obtener_por_clave(self, clave: str) -> dict | None:
        """
        Obtiene un producto por clave exacta.
        """
        if not clave:
            return None

        return self.col.find_one(
            {"clave": clave},
            self._projection()
        )

    # ─────────────────────────────────────────
    # BÚSQUEDA (AUTOCOMPLETADO)
    # ─────────────────────────────────────────
    def buscar(self, texto: str, limit: int = 10) -> list[dict]:
        """
        Busca productos por coincidencia parcial en clave o nombre.

        USO:
        - Autocompletado
        - Búsqueda flexible

        NOTAS:
        - No normaliza texto (responsabilidad del service)
        - Usa regex case-insensitive
        - Regex protegido contra caracteres especiales
        """
        if not texto:
            return []

        regex = re.escape(texto)

        query = {
            "$or": [
                {"clave": {"$regex": regex, "$options": "i"}},
                {"nombre": {"$regex": regex, "$options": "i"}},
            ]
        }

        cursor = (
            self.col
            .find(query, self._projection())
            .sort("nombre", 1)
            .limit(int(limit))
        )

        return list(cursor)
