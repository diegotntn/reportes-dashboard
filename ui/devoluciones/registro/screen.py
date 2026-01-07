from tkinter import ttk
from utils.scrollframe import ScrollFrame

from .form import RegistroForm
from .form import ArticuloForm
from .table import ArticulosTable
from .events import RegistroEvents


class RegistroScreen(ttk.Frame):
    """
    Contenedor principal del registro de devoluciones.
    """

    def __init__(self, parent, devoluciones_service, productos_service, on_saved=None):
        super().__init__(parent)

        # ───── Eventos / lógica ─────
        self.events = RegistroEvents(
            devoluciones_service=devoluciones_service,
            productos_service=productos_service,
            on_saved=on_saved
        )

        self._built = False
        self.build()

    def build(self):
        # Evitar duplicación visual
        if self._built:
            return
        self._built = True

        # Scroll principal
        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)

        frame = sf.inner

        # ─────────────────────────────
        # Datos de la devolución
        # ─────────────────────────────
        self.form = RegistroForm(frame)
        self.form.pack(fill="x", padx=12, pady=(12, 8))

        # ─────────────────────────────
        # Formulario para agregar artículo
        # ─────────────────────────────
        self.form_articulo = ArticuloForm(frame)
        self.form_articulo.pack(fill="x", padx=12, pady=(0, 8))

        # ─────────────────────────────
        # Tabla de artículos
        # ─────────────────────────────
        self.table = ArticulosTable(frame)
        self.table.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        # ─────────────────────────────
        # Botones
        # ─────────────────────────────
        btns = ttk.Frame(frame)
        btns.pack(fill="x", padx=12, pady=(0, 12))

        self.btn_agregar = ttk.Button(
            btns,
            text="Agregar artículo",
            command=self.events.on_agregar_articulo
        )
        self.btn_agregar.pack(side="left")

        self.btn_guardar = ttk.Button(
            btns,
            text="Guardar devolución",
            command=self.events.on_guardar
        )
        self.btn_guardar.pack(side="right")

        # ─────────────────────────────
        # Conectar eventos con UI
        # ─────────────────────────────
        self.events.bind(
            form=self.form,
            form_articulo=self.form_articulo,
            table=self.table,
            btn_guardar=self.btn_guardar,
            btn_agregar=self.btn_agregar
        )
