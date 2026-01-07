import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel

from ui.reportes.renderers.plotly import PlotlyKPI, PlotlyLine
from utils.helpers import money


class PersonasView(ttk.Frame):
    """
    Vista de análisis por PERSONA.

    PERSONA = personal operativo asignado a pasillos.

    RESPONSABILIDAD:
    - Mostrar KPIs por persona
    - Mostrar tendencia temporal por persona
    - Permitir seleccionar persona
    - SOLO renderiza (no calcula, no filtra)

    KPIs soportados:
    - Importe
    - Piezas
    - Total de devoluciones
    """

    TITLE = "Personas"

    # ─────────────────────────────
    def __init__(self, parent):
        super().__init__(parent)

        # ─────────────────────────
        # SELECTOR DE PERSONA
        # ─────────────────────────
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)

        ttk.Label(top, text="Persona:").pack(side="left", padx=5)

        self.persona_var = tk.StringVar()
        self.selector = ttk.Combobox(
            top,
            textvariable=self.persona_var,
            state="readonly",
            width=30
        )
        self.selector.pack(side="left")
        self.selector.bind("<<ComboboxSelected>>", self._on_change)

        # ─────────────────────────
        # CONTENEDORES
        # ─────────────────────────
        self.kpi_container = ttk.Frame(self)
        self.kpi_container.pack(fill="x", padx=8, pady=6)

        self.chart_container = ttk.Frame(self)
        self.chart_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ─────────────────────────
        # KPI RENDERERS
        # ─────────────────────────
        self.kpi_importe = PlotlyKPI()
        self.kpi_piezas = PlotlyKPI()
        self.kpi_devoluciones = PlotlyKPI()

        self.kpi_labels = {
            "importe": HTMLLabel(self.kpi_container),
            "piezas": HTMLLabel(self.kpi_container),
            "devoluciones": HTMLLabel(self.kpi_container),
        }

        for lbl in self.kpi_labels.values():
            lbl.pack(side="left", fill="x", expand=True, padx=6)

        # ─────────────────────────
        # CHART RENDERER
        # ─────────────────────────
        self.chart = PlotlyLine()

        self.chart_html = HTMLLabel(
            self.chart_container,
            background="white"
        )
        self.chart_html.pack(fill="both", expand=True)

        # Cache
        self._data_por_persona = {}
        self._kpis_flags = {}

    # ───────────────────────── API ─────────────────────────
    def render(self, resultado: dict) -> None:
        """
        Recibe el resultado completo del ReportesService.
        """
        self._data_por_persona = resultado.get("por_persona", {})
        self._kpis_flags = resultado.get("kpis", {})

        personas = sorted(self._data_por_persona.keys())

        if not personas:
            self._clear_all()
            self.selector["values"] = []
            self.persona_var.set("")
            return

        self.selector["values"] = personas

        if self.persona_var.get() not in personas:
            self.persona_var.set(personas[0])

        self._render_persona(self.persona_var.get())

    # ─────────────────────────
    def _on_change(self, _event=None) -> None:
        persona = self.persona_var.get()
        if persona:
            self._render_persona(persona)

    # ─────────────────────────
    def _render_persona(self, persona: str) -> None:
        """
        Renderiza una persona individual.

        data esperado:
        {
            "x": [...],
            "y": [...],
            "resumen": {
                "importe": float,
                "piezas": int,
                "devoluciones": int
            }
        }
        """
        data = self._data_por_persona.get(persona)
        if not data:
            self._clear_all()
            return

        resumen = data.get("resumen", {})
        x = data.get("x")
        y = data.get("y")

        if not x or not y:
            self._clear_all()
            return

        # ─────────────────────────
        # KPIs
        # ─────────────────────────
        if self._kpis_flags.get("importe"):
            self.kpi_importe.update(
                value=resumen.get("importe", 0),
                title="Importe",
                prefix="$"
            )
            self.kpi_labels["importe"].set_html(
                self.kpi_importe.to_html()
            )
        else:
            self.kpi_labels["importe"].set_html("")

        if self._kpis_flags.get("piezas"):
            self.kpi_piezas.update(
                value=resumen.get("piezas", 0),
                title="Piezas"
            )
            self.kpi_labels["piezas"].set_html(
                self.kpi_piezas.to_html()
            )
        else:
            self.kpi_labels["piezas"].set_html("")

        if self._kpis_flags.get("devoluciones"):
            self.kpi_devoluciones.update(
                value=resumen.get("devoluciones", 0),
                title="Devoluciones"
            )
            self.kpi_labels["devoluciones"].set_html(
                self.kpi_devoluciones.to_html()
            )
        else:
            self.kpi_labels["devoluciones"].set_html("")

        # ─────────────────────────
        # GRÁFICA
        # ─────────────────────────
        self.chart.update(
            x=x,
            y=y,
            title=f"Tendencia - {persona}"
        )

        self.chart_html.set_html(
            self.chart.to_html()
        )

    # ─────────────────────────
    # HELPERS
    # ─────────────────────────
    def _clear_all(self) -> None:
        """
        Limpia completamente la vista.
        """
        for lbl in self.kpi_labels.values():
            lbl.set_html("")

        self.chart_html.set_html("")
