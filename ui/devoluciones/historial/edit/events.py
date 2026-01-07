from tkinter import messagebox


class EditDevolucionEvents:
    """
    Eventos del diálogo de edición de devoluciones.

    RESPONSABILIDADES:
    - Coordinar acciones del formulario y la tabla
    - Eliminar artículos
    - Guardar cambios
    - Cerrar el diálogo correctamente

    NO HACE:
    - Dibujar UI
    - Acceder directamente a Mongo
    """

    def __init__(self, service, devolucion_id, on_saved=None, dialog=None):
        self.service = service
        self.devolucion_id = devolucion_id
        self.on_saved = on_saved
        self.dialog = dialog

        self.form = None
        self.table = None

    # ─────────────────────────────────────────────
    def bind(self, form, table):
        """
        Conecta formulario, tabla y botones del diálogo.
        """
        self.form = form
        self.table = table

        dialog = self.dialog

        # Validación defensiva
        if not dialog:
            raise RuntimeError("EditDevolucionEvents.bind(): dialog no inyectado")

        # Bind botones (referencias explícitas)
        dialog.btn_eliminar.configure(command=self._eliminar_articulo)
        dialog.btn_guardar.configure(command=self._guardar)
        dialog.btn_cancelar.configure(command=dialog.destroy)

    # ─────────────────────────────────────────────
    def _eliminar_articulo(self):
        """
        Elimina el artículo seleccionado de la tabla.
        """
        item_id = self.table.selected_item_id()
        if not item_id:
            messagebox.showwarning(
                "Selecciona un artículo",
                "Debes seleccionar un artículo para eliminar."
            )
            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar el artículo seleccionado?"
        ):
            return

        self.table.remove_item(item_id)

    # ─────────────────────────────────────────────
    def _guardar(self):
        """
        Guarda los cambios de la devolución.

        Reglas:
        - Si NO se modificaron artículos → NO se envían
        - Si se modificaron → deben ser válidos
        """
        try:
            data = self.form.get_data()
        except Exception as e:
            messagebox.showerror("Datos inválidos", str(e))
            return

        items = None

        # 👉 SOLO enviar artículos si fueron modificados
        if self.table.was_modified():
            items = self.table.get_items()

            if not items:
                messagebox.showwarning(
                    "Sin artículos",
                    "La devolución debe tener al menos un artículo."
                )
                return

        try:
            self.service.actualizar(
                devolucion_id=self.devolucion_id,
                **data,
                items=items,   # ← None si NO hubo cambios
            )
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return

        if callable(self.on_saved):
            self.on_saved()

        self.dialog.destroy()
