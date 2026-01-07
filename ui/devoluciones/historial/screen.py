from tkinter import ttk

from .filters import HistorialFilters
from .table import HistorialTables
from .events import HistorialEvents

from ui.devoluciones.historial.edit.dialog import EditDevolucionDialog


class HistorialScreen(ttk.Frame):
    """
    Pantalla principal del historial de devoluciones.
    """

    def __init__(self, parent, devoluciones_service, on_change=None):
        super().__init__(parent)

        self.service = devoluciones_service
        self.on_change = on_change

        # Events
        self.events = HistorialEvents(
            devoluciones_service=self.service,
            on_change=self.on_change
        )

        self.build()

    # ─────────────────────────────────────────────
    def build(self):
        cont = ttk.Frame(self, padding=12)
        cont.pack(fill="both", expand=True)

        # Filtros
        self.filters = HistorialFilters(cont)
        self.filters.pack(fill="x")

        # Acciones
        actions = ttk.Frame(cont)
        actions.pack(fill="x", pady=(6, 4))

        ttk.Button(
            actions,
            text="Actualizar historial",
            command=self.events.cargar_historial
        ).pack(anchor="e")

        # Tabla
        self.tables = HistorialTables(cont)
        self.tables.pack(fill="both", expand=True, pady=(10, 0))

        # 🔑 AQUÍ ESTABA EL ERROR:
        # se debe pasar explícitamente el callback open_editor
        self.events.bind(
            filters=self.filters,
            tables=self.tables,
            open_editor=self._open_editor
        )

        # Carga inicial
        self.events.cargar_historial()

    # ─────────────────────────────────────────────
    def _open_editor(self, devolucion_id, devol_row):
        """
        Abre la ventana modal de edición.

        RESPONSABILIDAD:
        - Obtener los artículos de la devolución (lectura)
        - Asignar explícitamente el retorno
        - Abrir el diálogo con datos válidos
        """

        # 1️⃣ Obtener artículos (OBLIGATORIO asignar)
        arts_df = self.service.obtener_articulos(devolucion_id)

        # 2️⃣ Validación defensiva (contrato)
        if arts_df is None:
            raise RuntimeError(
                "_open_editor recibió arts_df=None desde el service. "
                "Revisa obtener_articulos()."
            )

        # 3️⃣ Abrir diálogo
        EditDevolucionDialog(
            parent=self,
            service=self.service,
            devolucion_id=devolucion_id,
            devol_row=devol_row,
            arts_df=arts_df,
            on_saved=self._on_saved,
        )

    # ─────────────────────────────────────────────
    def _on_saved(self):
        """
        Callback cuando se guarda una devolución.
        """
        self.events.cargar_historial()

        if self.on_change:
            self.on_change()
