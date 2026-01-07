import pandas as pd
import re


class ProductosRepo:
    """
    Repositorio MongoDB para productos.

    Responsabilidades:
    - Consultar productos
    - NO contiene lógica de negocio
    - NO conoce UI
    """

    def __init__(self, db):
        """
        db: instancia de MongoDB (client.db)
        """
        self.col = db.productos

    # ─────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────
    @staticmethod
    def _df(docs):
        """
        Convierte una lista de documentos en DataFrame.
        """
        return pd.DataFrame(docs) if docs else pd.DataFrame()

    @staticmethod
    def _projection():
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
        return self._df(docs)

    # ─────────────────────────────────────────
    # OBTENER POR CLAVE EXACTA
    # ─────────────────────────────────────────
    def get_por_clave(self, clave: str):
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
    # BÚSQUEDA PARA AUTOCOMPLETADO
    # ─────────────────────────────────────────
    def buscar_por_clave_o_nombre(self, texto: str, limit: int = 10):
        """
        Busca productos por coincidencia parcial en clave o nombre.
        Usado para autocompletado.

        - No normaliza texto (eso es responsabilidad del service)
        - Usa regex case-insensitive
        """
        if not texto:
            return []

        # Regex seguro (evita errores por caracteres especiales)
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
            .limit(limit)
        )

        return list(cursor)

