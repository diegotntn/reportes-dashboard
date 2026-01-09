"""
Service de Devoluciones.

RESPONSABILIDAD:
- Punto único de acceso a la lógica de devoluciones
- Orquestar commands y queries
- Mantener estable la API de negocio

NO HACE:
- Validaciones de dominio
- Acceso directo a MongoDB
- Lógica de UI
"""

# ───────────────────────── COMMANDS (ESCRITURA) ─────────────────────────
from backend.services.devoluciones.commands.crear_devolucion import (
    crear_devolucion,
)
from backend.services.devoluciones.commands.actualizar_devolucion import (
    actualizar_devolucion,
)
from backend.services.devoluciones.commands.cambiar_estatus import (
    cambiar_estatus,
)
from backend.services.devoluciones.commands.eliminar_devolucion import (
    eliminar_devolucion,
)

# ───────────────────────── QUERIES (LECTURA) ─────────────────────────
from backend.services.devoluciones.queries.listar_historial import (
    listar_historial,
)
from backend.services.devoluciones.queries.obtener_articulos import (
    obtener_articulos,
)
from backend.services.devoluciones.queries.obtener_completa import (
    obtener_completa,
)


class DevolucionesService:
    """
    Service de negocio para devoluciones.

    LA API:
    - La UI y scripts SOLO hablan con esta clase
    - NO conoce MongoDB
    - NO conoce pandas
    - NO conoce detalles de implementación
    """

    def __init__(self, devoluciones_repo, reportes_queries):
        """
        Parámetros
        ----------
        devoluciones_repo : DevolucionesRepo
            Repositorio de devoluciones (CRUD y lecturas simples)
        reportes_queries : ReportesQueries
            Queries especializadas (agregaciones y lecturas complejas)

        NOTA CRÍTICA:
        - reportes_queries DEBE recibir una Collection Mongo
        - NUNCA un Database
        """
        self.repo = devoluciones_repo
        self.reportes_queries = reportes_queries

    # ───────────────────────── REGISTRO ─────────────────────────
    def registrar(
        self,
        *,
        fecha,
        folio,
        cliente,
        direccion,
        motivo,
        zona,
        items,
        vendedor_id=None,
    ):
        """
        Registra una devolución nueva.

        Flujo:
        API → Service → Command → Dominio → Repo
        """
        return crear_devolucion(
            repo=self.repo,
            fecha=fecha,
            folio=folio,
            cliente=cliente,
            direccion=direccion,
            motivo=motivo,
            zona=zona,
            items=items,
            vendedor_id=vendedor_id,
        )

    # ───────────────────────── HISTORIAL ─────────────────────────
    def listar(self, *, desde=None, hasta=None, **filtros):
        """
        Devuelve el historial de devoluciones
        para tablas y reportes.
        """
        return listar_historial(
            repo=self.repo,
            desde=desde,
            hasta=hasta,
            **filtros,
        )

    # ───────────────────────── CONSULTAS ─────────────────────────
    def obtener_articulos(self, devolucion_id: str):
        """
        Devuelve los artículos de una devolución.

        NOTA:
        - El Service solo orquesta
        - La lógica vive en Queries
        """
        return obtener_articulos(
            reportes_queries=self.reportes_queries,
            devolucion_id=devolucion_id,
        )

    def obtener_completa(self, devolucion_id: str):
        """
        Devuelve la devolución completa para edición.
        """
        return obtener_completa(
            repo=self.repo,
            devolucion_id=devolucion_id,
        )

    # ───────────────────────── ACTUALIZAR ─────────────────────────
    def actualizar(self, *, devolucion_id: str, **data):
        """
        Actualiza una devolución existente.
        """
        return actualizar_devolucion(
            repo=self.repo,
            devolucion_id=devolucion_id,
            **data,
        )

    # ───────────────────────── ESTATUS ─────────────────────────
    def cambiar_estatus(self, devolucion_id: str, nuevo_estatus: str):
        """
        Cambia el estatus de una devolución.
        """
        return cambiar_estatus(
            repo=self.repo,
            devolucion_id=devolucion_id,
            nuevo_estatus=nuevo_estatus,
        )

    # ───────────────────────── ELIMINAR ─────────────────────────
    def eliminar(self, devolucion_id: str):
        """
        Elimina una devolución.
        """
        return eliminar_devolucion(
            repo=self.repo,
            devolucion_id=devolucion_id,
        )
