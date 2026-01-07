from domain.productos import Producto
from utils.helpers import normalizar_texto_busqueda


class ProductosService:
    """
    Lógica de negocio para productos.

    Responsabilidades:
    - Buscar productos (autocomplete)
    - Obtener producto por clave
    - Normalizar estructura del producto
    - Centralizar reglas relacionadas con productos

    NO contiene:
    - UI
    - SQL
    - Tkinter
    """

    def __init__(self, productos_repo):
        """
        productos_repo: instancia de ProductosRepo
        """
        self.repo = productos_repo

    # ─────────────────────────────────────────
    # BÚSQUEDA PARA AUTOCOMPLETADO
    # ─────────────────────────────────────────
    def buscar_por_clave_o_nombre(self, texto: str, limit: int = 10):
        """
        Busca productos por coincidencia parcial en clave o nombre.

        Reglas:
        - mínimo 2 caracteres
        - busca por clave OR nombre
        - devuelve lista de dicts normalizados
        """
        texto = normalizar_texto_busqueda(texto)

        if len(texto) < 2:
            return []

        productos = self.repo.buscar_por_clave_o_nombre(texto, limit)
        return self._normalizar_lista(productos)

    # ─────────────────────────────────────────
    # ALIAS DE BÚSQUEDA
    # ─────────────────────────────────────────
    def buscar(self, texto: str, limit: int = 10):
        """
        Alias de buscar_por_clave_o_nombre.
        """
        return self.buscar_por_clave_o_nombre(texto, limit)

    # ─────────────────────────────────────────
    # OBTENER PRODUCTO POR CLAVE EXACTA
    # ─────────────────────────────────────────
    def obtener_por_clave(self, clave: str):
        """
        Obtiene un producto específico por su clave exacta.
        """
        clave = normalizar_texto_busqueda(clave)
        if not clave:
            return None

        p = self.repo.get_por_clave(clave)
        if not p:
            return None

        prod = Producto.from_dict(p)
        return prod.normalizado()

    # ─────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────
    def _normalizar_lista(self, productos):
        """
        Convierte lista de dicts crudos en productos normalizados.
        Productos inválidos se ignoran silenciosamente.
        """
        normalizados = []

        for p in productos:
            try:
                prod = Producto.from_dict(p)
                normalizados.append(prod.normalizado())
            except ValueError:
                # Producto inválido → se ignora
                continue

        return normalizados
