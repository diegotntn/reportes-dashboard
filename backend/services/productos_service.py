from backend.domain.productos import Producto
from backend.services.shared.texto import normalizar_texto_busqueda


class ProductosService:
    """
    Lógica de negocio para productos.

    RESPONSABILIDADES:
    - Buscar productos (autocomplete)
    - Obtener producto por clave exacta
    - Normalizar estructura del producto
    - Centralizar reglas relacionadas con productos

    NO contiene:
    - UI
    - Acceso a BD
    - Frameworks (FastAPI, Tkinter, etc.)
    """

    def __init__(self, productos_repo):
        """
        Parámetros
        ----------
        productos_repo : ProductosRepo
            Repositorio de acceso a datos de productos.
        """
        self.repo = productos_repo

    # ─────────────────────────────────────────
    # BÚSQUEDA (AUTOCOMPLETADO)
    # ─────────────────────────────────────────
    def buscar(self, texto: str, limit: int = 10):
        """
        Busca productos por coincidencia parcial en clave o nombre.

        REGLAS DE NEGOCIO:
        - Normaliza el texto de búsqueda
        - Mínimo 2 caracteres
        - Devuelve lista de productos normalizados
        """
        texto = normalizar_texto_busqueda(texto)

        if not texto or len(texto) < 2:
            return []

        productos = self.repo.buscar(texto, limit)
        return self._normalizar_lista(productos)

    # ─────────────────────────────────────────
    # OBTENER PRODUCTO POR CLAVE EXACTA
    # ─────────────────────────────────────────
    def obtener_por_clave(self, clave: str):
        """
        Obtiene un producto por su clave exacta.
        """
        clave = normalizar_texto_busqueda(clave)

        if not clave:
            return None

        p = self.repo.obtener_por_clave(clave)
        if not p:
            return None

        prod = Producto.from_dict(p)
        return prod.normalizado()

    # ─────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────
    def _normalizar_lista(self, productos: list[dict]) -> list[dict]:
        """
        Convierte una lista de documentos crudos en productos normalizados.

        NOTA:
        - Productos inválidos se ignoran silenciosamente
        """
        normalizados = []

        for p in productos:
            try:
                prod = Producto.from_dict(p)
                normalizados.append(prod.normalizado())
            except ValueError:
                # Documento inválido → se ignora
                continue

        return normalizados
