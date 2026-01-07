import tkinter as tk
from tkinter import ttk
from datetime import date

from tkcalendar import DateEntry


class FiltersPanel(ttk.Frame):
    """
    Panel de filtros GLOBAL de reportes.

    RESPONSABILIDADES:
    - Capturar filtros visuales
    - Exponerlos como dict plano para el Service
    - Manejar estado de loading (UI)

    NO hace:
    - Cálculos
    - Consultas
    - Transformaciones de datos
    """

    def __init__(self, parent, on_change):
        super().__init__(parent)

        self.on_change = on_change

        # variables UI
        self._init_vars()

        # construcción visual
        self._build()

    # ─────────────────────────────
    # VARIABLES
    # ─────────────────────────────
    def _init_vars(self):
        """Variables Tkinter (estado del panel)."""

        # fechas
        self.desde = tk.StringVar()
        self.hasta = tk.StringVar()

        # agrupación temporal
        self.agrupar = tk.StringVar(value="Mes")

        # KPIs visibles
        self.kpi_importe = tk.BooleanVar(value=True)
        self.kpi_piezas = tk.BooleanVar(value=True)
        self.kpi_devoluciones = tk.BooleanVar(value=True)

    # ─────────────────────────────
    # UI
    # ─────────────────────────────
    def _build(self):
        # ───── Fechas ─────
        ttk.Label(self, text="Desde").grid(row=0, column=0, sticky="w")

        self.dt_desde = DateEntry(
            self,
            textvariable=self.desde,
            date_pattern="yyyy-mm-dd",
            width=12
        )
        self.dt_desde.set_date(date.today().replace(day=1))
        self.dt_desde.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(self, text="Hasta").grid(row=0, column=2, sticky="w")

        self.dt_hasta = DateEntry(
            self,
            textvariable=self.hasta,
            date_pattern="yyyy-mm-dd",
            width=12
        )
        self.dt_hasta.set_date(date.today())
        self.dt_hasta.grid(row=0, column=3, padx=(0, 16))

        # ───── Agrupación ─────
        ttk.Label(self, text="Agrupar por").grid(row=0, column=4, sticky="w")

        ttk.Combobox(
            self,
            textvariable=self.agrupar,
            values=["Día", "Semana", "Mes", "Año"],
            state="readonly",
            width=8
        ).grid(row=0, column=5, padx=(0, 16))

        # ───── KPIs ─────
        kpi_frame = ttk.LabelFrame(self, text="KPIs visibles", padding=(8, 4))
        kpi_frame.grid(row=0, column=6, padx=(0, 16))

        ttk.Checkbutton(
            kpi_frame,
            text="Importe",
            variable=self.kpi_importe
        ).pack(side="left", padx=6)

        ttk.Checkbutton(
            kpi_frame,
            text="Piezas",
            variable=self.kpi_piezas
        ).pack(side="left", padx=6)

        ttk.Checkbutton(
            kpi_frame,
            text="Devoluciones",
            variable=self.kpi_devoluciones
        ).pack(side="left", padx=6)

        # ───── Acción ─────
        self.btn_actualizar = ttk.Button(
            self,
            text="Actualizar",
            command=self.on_change
        )
        self.btn_actualizar.grid(row=0, column=7, padx=5)

    # ─────────────────────────────
    # API PÚBLICA (para ReportesTab)
    # ─────────────────────────────
    def get(self):
        """
        Devuelve filtros GLOBALS listos para el Service.
        """
        return {
            "desde": self.desde.get(),
            "hasta": self.hasta.get(),
            "agrupar": self.agrupar.get(),
            "kpis": {
                "importe": self.kpi_importe.get(),
                "piezas": self.kpi_piezas.get(),
                "devoluciones": self.kpi_devoluciones.get(),
            }
        }

    def set_loading(self):
        """Deshabilita UI mientras se calculan reportes."""
        self.btn_actualizar.state(["disabled"])
        self.winfo_toplevel().config(cursor="watch")

    def clear_loading(self):
        """Restaura UI después del cálculo."""
        self.btn_actualizar.state(["!disabled"])
        self.winfo_toplevel().config(cursor="")
