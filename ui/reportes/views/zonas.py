import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel

from ui.reportes.renderers.plotly import PlotlyKPI, PlotlyLine
from utils.scrollframe import ScrollFrame
from utils.helpers import money


class ZonasView(ttk.Frame):
    """
    Vista de análisis por ZONA.

    RESPONSABILIDAD:
    - Mostrar KPIs por zona
    - Mostrar tendencia temporal por zona
    - Permitir seleccionar zonas visibles
    - SOLO renderiza (no calcula, no filtra)

    KPIs soportados:
    - Importe
    - Piezas
    - Total de devoluciones
    """

    TITLE = "Zonas"

    def __init__(self, parent):
        super().__init__(parent)

        # ─────────────────────────
        # SELECTOR DE ZONAS
        # ─────────────────────────
        self.selector_frame = ttk.LabelFrame(
            self, text="Zonas visibles", padding=6
        )
        self.selector_frame.pack(fill="x", padx=10, pady=(6, 2))

        self._zona_vars = {}

        # ─────────────────────────
        # SCROLL PRINCIPAL
        # ─────────────────────────
        self.scroll = ScrollFrame(self)
        self.scroll.pack(fill="both", expand=True)

        self.container = self.scroll.frame

        # Cache de datos
        self._data_por_zona = {}
        self._kpis_flags = {}

    # ───────────────────────── API ─────────────────────────
    def render(self, resultado: dict) -> None:
        """
        Recibe resultado completo del ReportesService.
        """
        self._data_por_zona = resultado.get("por_zona", {})
        self._kpis_flags = resultado.get("kpis", {})

        zonas = sorted(self._data_por_zona.keys())

        # Limpiar selector y contenido
        for w in self.selector_frame.winfo_children():
            w.destroy()
        for w in self.container.winfo_children():
            w.destroy()

        if not zonas:
            ttk.Label(
                self.container,
                text="No hay datos para mostrar"
            ).pack(pady=20)
            return

        # ─────────────────────────
        # CONSTRUIR SELECTOR
        # ─────────────────────────
        self._zona_vars.clear()

        for zona in zonas:
            var = tk.BooleanVar(value=True)
            self._zona_vars[zona] = var

            ttk.Checkbutton(
                self.selector_frame,
                text=zona,
                variable=var,
                command=self._refrescar_zonas
            ).pack(side="left", padx=6)

        ttk.Button(
            self.selector_frame,
            text="Todas",
            command=self._seleccionar_todas
        ).pack(side="right", padx=4)

        ttk.Button(
            self.selector_frame,
            text="Ninguna",
            command=self._deseleccionar_todas
        ).pack(side="right", padx=4)

        # Render inicial
        self._refrescar_zonas()

    # ─────────────────────────
    def _refrescar_zonas(self) -> None:
        """
        Renderiza únicamente las zonas seleccionadas.
        """
        for w in self.container.winfo_children():
            w.destroy()

        visibles = [
            z for z, v in self._zona_vars.items() if v.get()
        ]

        if not visibles:
            ttk.Label(
                self.container,
                text="Selecciona al menos una zona"
            ).pack(pady=20)
            return

        for zona in visibles:
            self._render_zona(zona, self._data_por_zona.get(zona, {}))

    # ─────────────────────────
    def _seleccionar_todas(self) -> None:
        for v in self._zona_vars.values():
            v.set(True)
        self._refrescar_zonas()

    def _deseleccionar_todas(self) -> None:
        for v in self._zona_vars.values():
            v.set(False)
        self._refrescar_zonas()

    # ─────────────────────────
    def _render_zona(self, zona: str, data: dict) -> None:
        """
        Renderiza una zona individual.

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

        resumen = data.get("resumen", {})
        x = data.get("x")
        y = data.get("y")

        if not x or not y:
            return

        # ─────────────────────────
        # CONTENEDOR POR ZONA
        # ─────────────────────────
        frame = ttk.LabelFrame(
            self.container,
            text=f"Zona: {zona}",
            padding=8
        )
        frame.pack(fill="x", padx=10, pady=10)

        # ─────────────────────────
        # KPIs
        # ─────────────────────────
        kpi_container = ttk.Frame(frame)
        kpi_container.pack(fill="x", pady=6)

        kpi_importe = PlotlyKPI()
        kpi_piezas = PlotlyKPI()
        kpi_devoluciones = PlotlyKPI()

        kpi_labels = {
            "importe": HTMLLabel(kpi_container),
            "piezas": HTMLLabel(kpi_container),
            "devoluciones": HTMLLabel(kpi_container),
        }

        for lbl in kpi_labels.values():
            lbl.pack(side="left", fill="x", expand=True, padx=6)

        if self._kpis_flags.get("importe"):
            kpi_importe.update(
                value=resumen.get("importe", 0),
                title="Importe",
                prefix="$"
            )
            kpi_labels["importe"].set_html(kpi_importe.to_html())

        if self._kpis_flags.get("piezas"):
            kpi_piezas.update(
                value=resumen.get("piezas", 0),
                title="Piezas"
            )
            kpi_labels["piezas"].set_html(kpi_piezas.to_html())

        if self._kpis_flags.get("devoluciones"):
            kpi_devoluciones.update(
                value=resumen.get("devoluciones", 0),
                title="Devoluciones"
            )
            kpi_labels["devoluciones"].set_html(
                kpi_devoluciones.to_html()
            )

        # ─────────────────────────
        # GRÁFICA DE TENDENCIA
        # ─────────────────────────
        chart = PlotlyLine()

        chart_html = HTMLLabel(
            frame,
            background="white"
        )
        chart_html.pack(fill="x", pady=(6, 0))

        chart.update(
            x=x,
            y=y,
            title=f"Tendencia - Zona {zona}"
        )

        chart_html.set_html(chart.to_html())
