from tkinter import messagebox
from utils.helpers import pasillo_desde_linea, normalizar_texto_busqueda


class RegistroEvents:
    """
    Callbacks y lógica de interacción del registro de devoluciones.
    Orquesta UI ↔ Services ↔ Dominio.
    """

    def __init__(self, devoluciones_service, productos_service, on_saved=None):
        self.devoluciones_service = devoluciones_service
        self.productos_service = productos_service
        self.on_saved = on_saved

        self.form = None
        self.form_articulo = None
        self.table = None

        self._btn_guardar = None
        self._btn_agregar = None

        # cache resultados autocomplete
        self._resultados = []

    # ─────────────────────────────────────────
    # BINDING UI
    # ─────────────────────────────────────────
    def bind(
        self,
        form,
        form_articulo,
        table,
        btn_guardar=None,
        btn_agregar=None
    ):
        self.form = form
        self.form_articulo = form_articulo
        self.table = table

        self._btn_guardar = btn_guardar
        self._btn_agregar = btn_agregar

        if self._btn_guardar:
            self._btn_guardar.config(state="disabled")

        # Escuchar escritura (autocomplete)
        self.form_articulo.buscar_var.trace_add(
            "write",
            self._on_buscar_producto
        )

        # Eventos listbox
        lb = self.form_articulo._listbox
        lb.bind("<Double-Button-1>", self._on_listbox_click)
        lb.bind("<Return>", self._on_listbox_enter)

        # Teclas en buscador
        self.form_articulo.buscar.bind("<Down>", self._focus_listbox)
        self.form_articulo.buscar.bind("<Escape>", self._ocultar_sugerencias)

    # ─────────────────────────────────────────
    # AUTOCOMPLETADO
    # ─────────────────────────────────────────
    def _on_buscar_producto(self, *_):
        texto = normalizar_texto_busqueda(
            self.form_articulo.buscar_var.get()
        )

        if len(texto) < 2:
            self._resultados = []
            self.form_articulo.ocultar_sugerencias()
            return

        self._resultados = (
            self.productos_service.buscar_por_clave_o_nombre(texto)
            or []
        )

        self.form_articulo.mostrar_sugerencias(self._resultados)

    def _focus_listbox(self, _event=None):
        if self._resultados:
            self.form_articulo._listbox.focus_set()
            self.form_articulo._listbox.selection_set(0)

    def _on_listbox_click(self, _event=None):
        self._seleccionar_actual()

    def _on_listbox_enter(self, _event=None):
        self._seleccionar_actual()

    def _seleccionar_actual(self):
        lb = self.form_articulo._listbox
        sel = lb.curselection()

        if not sel:
            return

        producto = self._resultados[sel[0]]

        pasillo = pasillo_desde_linea(producto.get("linea"))

        self.form_articulo.set_producto(
            producto=producto,
            pasillo=pasillo
        )

        self.form_articulo.ocultar_sugerencias()

    def _ocultar_sugerencias(self, _event=None):
        self.form_articulo.ocultar_sugerencias()

    # ─────────────────────────────────────────
    # AGREGAR ARTÍCULO
    # ─────────────────────────────────────────
    def on_agregar_articulo(self):
        try:
            data = self.form_articulo.get_data()

            if not data["clave"]:
                raise ValueError("Selecciona un producto válido")

            if not data["pasillo"]:
                raise ValueError("Debes seleccionar el pasillo")

            self.table.add_item(
                clave=data["clave"],
                descripcion=data["nombre"],
                cantidad=data["cantidad"],
                precio=data["precio"],
                pasillo=data["pasillo"],
            )

            self.form_articulo.clear()

            if self._btn_guardar:
                self._btn_guardar.config(state="normal")

        except ValueError as e:
            messagebox.showwarning("Error", str(e))

    # ─────────────────────────────────────────
    # GUARDAR DEVOLUCIÓN
    # ─────────────────────────────────────────
    def on_guardar(self):
        try:
            data = self.form.get_data()
            items = self.table.get_items()

            if not items:
                raise ValueError("No hay artículos agregados")

            self.devoluciones_service.registrar(
                **data,
                items=items
            )

        except ValueError as e:
            messagebox.showwarning("Error", str(e))
            return

        messagebox.showinfo("OK", "Devolución guardada correctamente")

        # Reset UI
        self.form.clear()
        self.form_articulo.clear()
        self.table.clear()

        if self._btn_guardar:
            self._btn_guardar.config(state="disabled")

        if self.on_saved:
            self.on_saved()
