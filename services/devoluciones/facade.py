"""
Fachada de Devoluciones.

RESPONSABILIDAD:
- Ser el ÚNICO punto de acceso desde la UI
- Delegar a casos de uso (commands / queries)
- Mantener estable la API aunque cambie la implementación interna

NO HACE:
- Validaciones de negocio (eso es dominio)
- Acceso directo a Mongo (eso es DB / queries)
- Transformaciones de datos complejas (eso es queries / mappers)
"""

# ───────────────────────── COMMANDS (ESCRITURA) ─────────────────────────
from services.devoluciones.commands.crear_devolucion import crear_devolucion
from services.devoluciones.commands.actualizar_devolucion import actualizar_devolucion
from services.devoluciones.commands.cambiar_estatus import cambiar_estatus
from services.devoluciones.commands.eliminar_devolucion import eliminar_devolucion

# ───────────────────────── QUERIES (LECTURA) ─────────────────────────
from services.devoluciones.queries.listar_historial import listar_historial
from services.devoluciones.queries.obtener_articulos import obtener_articulos
from services.devoluciones.queries.obtener_completa import obtener_completa


class DevolucionesService:
    """
    Fachada pública usada por la UI.

    La UI:
    - SOLO habla con esta clase
    - NO conoce repositorios
    - NO conoce Mongo
    - NO conoce pandas
    """

    def __init__(self, db, reportes_queries):
        """
        Parámetros:
        - db: BaseDB (Mongo / SQLite)
        - reportes_queries: ReportesQueries (lecturas especializadas con aggregations)
        """
        self.db = db
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
        UI → Facade → Command → Dominio → Persistencia
        """
        return crear_devolucion(
            db=self.db,
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
        para la tabla principal.
        """
        return listar_historial(
            db=self.db,
            desde=desde,
            hasta=hasta,
            **filtros,
        )

    def obtener_articulos(self, devolucion_id: str):
        """
        Devuelve los artículos de una devolución como DataFrame.

        NOTA:
        - La UI NUNCA debe llamar a queries directamente
        - Este método garantiza un DataFrame válido (nunca None)
        """
        return obtener_articulos(
            self.reportes_queries,  # llamada POSICIONAL (correcta)
            devolucion_id,
        )

    def obtener_completa(self, devolucion_id: str):
        """
        Devuelve la devolución completa para edición.

        Retorna una estructura del tipo:
        {
            "fecha": ...,
            "folio": ...,
            "cliente": ...,
            ...
            "items": [...],
            "articulos_df": pandas.DataFrame
        }
        """
        return obtener_completa(
            db=self.db,
            devolucion_id=devolucion_id,
        )

    # ───────────────────────── ACTUALIZAR ─────────────────────────
    def actualizar(self, *, devolucion_id: str, **data):
        """
        Actualiza una devolución existente.

        Puede recibir:
        - Datos de encabezado (fecha, folio, cliente, etc.)
        - items: lista de artículos actualizados

        La fachada NO interpreta los datos.
        """
        return actualizar_devolucion(
            db=self.db,
            devolucion_id=devolucion_id,
            **data,   # ← aquí ya es válido que venga `items`
        )

    # ───────────────────────── ESTATUS ─────────────────────────
    def cambiar_estatus(self, devolucion_id: str, nuevo_estatus: str):
        """
        Cambia el estatus de una devolución
        (pendiente, cerrada, cancelada, etc.).
        """
        return cambiar_estatus(
            db=self.db,
            devolucion_id=devolucion_id,
            nuevo_estatus=nuevo_estatus,
        )

    # ───────────────────────── ELIMINAR ─────────────────────────
    def eliminar(self, devolucion_id: str):
        """
        Elimina una devolución.
        """
        return eliminar_devolucion(
            db=self.db,
            devolucion_id=devolucion_id,
        )
