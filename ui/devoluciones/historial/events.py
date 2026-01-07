from tkinter import messagebox


class HistorialEvents:
    """
    Eventos del historial de devoluciones.

    RESPONSABILIDADES:
    - Leer filtros desde la UI
    - Cargar historial
    - Detectar interacción (doble clic)
    - Preparar datos mínimos para abrir editor

    NO HACE:
    - Dibujar widgets
    - Acceder a Mongo directamente
    - Guardar devoluciones
    - Manipular artículos
    """

    def __init__(self, devoluciones_service, on_change=None):
        self.service = devoluciones_service
        self.on_change = on_change

        self.filters = None
        self.tables = None
        self._open_editor = None  # callback inyectado desde Screen

    # ─────────────────────────────────────────────
    def bind(self, filters, tables, open_editor):
        """
        Conecta filtros, tablas y callbacks.
        """
        self.filters = filters
        self.tables = tables
        self._open_editor = open_editor

        if not self.tables or not hasattr(self.tables, "devol_tree"):
            raise RuntimeError(
                "HistorialEvents.bind(): tables inválido o sin devol_tree"
            )

        # 👉 Doble clic = abrir editor
        self.tables.devol_tree.bind(
            "<Double-1>",
            self._on_double_click
        )

    # ─────────────────────────────────────────────
    def cargar_historial(self):
        """
        Carga o recarga el historial según filtros.
        """
        if not self.filters or not self.tables:
            return

        try:
            filtros = self.filters.get_filtros()
            desde = filtros.get("desde")
            hasta = filtros.get("hasta")
        except ValueError as e:
            messagebox.showwarning("Fechas inválidas", str(e))
            return

        df = self.service.listar(
            desde=desde,
            hasta=hasta
        )

        self.tables.clear()

        if df is None or df.empty:
            return

        for _, row in df.iterrows():
            self.tables.insert_devolucion(row)

    # ─────────────────────────────────────────────
    def _on_double_click(self, event):
        """
        Maneja doble clic sobre una fila válida.
        """
        if not self.tables:
            return

        tree = self.tables.devol_tree

        row_id = tree.identify_row(event.y)
        if not row_id:
            return

        # Forzar selección visual
        tree.selection_set(row_id)
        tree.focus(row_id)

        self._abrir_editor(row_id)

    # ─────────────────────────────────────────────
    def _abrir_editor(self, devolucion_id):
        """
        Prepara encabezado y delega apertura del editor.

        IMPORTANTE:
        - NO carga artículos
        - NO pasa artículos
        - El editor decide qué hacer después
        """
        if not devolucion_id:
            return

        data = self.service.obtener_completa(devolucion_id)

        if not data:
            messagebox.showerror(
                "Error",
                "No se encontró la devolución."
            )
            return

        # Encabezado (solo datos del formulario)
        devol_row = {
            "fecha": data.get("fecha"),
            "folio": data.get("folio"),
            "cliente": data.get("cliente"),
            "direccion": data.get("direccion"),
            "motivo": data.get("motivo"),
            "zona": data.get("zona"),
            "total": data.get("total"),
            "estatus": data.get("estatus"),
        }

        if callable(self._open_editor):
            # 👉 SOLO id + encabezado
            self._open_editor(
                devolucion_id,
                devol_row
            )

    # ─────────────────────────────────────────────
    def eliminar(self):
        """
        Elimina la devolución seleccionada.
        """
        if not self.tables:
            return

        devolucion_id = self.tables.selected_devolucion_id()
        if not devolucion_id:
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar esta devolución?"
        ):
            return

        self.service.eliminar(devolucion_id)

        # Recargar historial
        self.cargar_historial()

        if callable(self.on_change):
            self.on_change()
