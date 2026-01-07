from tkinter import ttk


class PersonalTables(ttk.Frame):
    """
    Tablas:
    - Personal operativo
    - Asignaciones registradas
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        self._build_personal()
        self._build_asignaciones()

    # ───────── PERSONAL OPERATIVO ─────────
    def _build_personal(self):
        f = ttk.LabelFrame(self, text="Personal operativo", padding=10)
        f.pack(fill="x")

        self.tbl_personal = ttk.Treeview(
            f,
            columns=("id", "nombre"),
            show="headings",
            height=6
        )

        # Encabezados
        self.tbl_personal.heading("nombre", text="Nombre")

        # Columnas
        self.tbl_personal.column("id", width=0, stretch=False)   # id oculto
        self.tbl_personal.column("nombre", width=420, anchor="w")

        self.tbl_personal.pack(fill="x")

    # ───────── ASIGNACIONES ─────────
    def _build_asignaciones(self):
        f = ttk.LabelFrame(self, text="Asignaciones registradas", padding=10)
        f.pack(fill="both", expand=True, pady=(10, 0))

        # 🔑 ORDEN CORRECTO DE COLUMNAS (SIN id)
        self.tbl_asig = ttk.Treeview(
            f,
            columns=("pasillo", "persona", "desde", "hasta"),
            show="headings",
            height=8
        )

        # Encabezados
        self.tbl_asig.heading("pasillo", text="Pasillo")
        self.tbl_asig.heading("persona", text="Persona")
        self.tbl_asig.heading("desde", text="Desde")
        self.tbl_asig.heading("hasta", text="Hasta")

        # Columnas
        self.tbl_asig.column("pasillo", width=90, anchor="center")
        self.tbl_asig.column("persona", width=260, anchor="w")
        self.tbl_asig.column("desde", width=120, anchor="center")
        self.tbl_asig.column("hasta", width=120, anchor="center")

        self.tbl_asig.pack(fill="both", expand=True)
