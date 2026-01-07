import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel

from ui.reportes.renderers.plotly import PlotlyKPI, PlotlyLine
from utils.helpers import money


class PasillosView(ttk.Frame):
    """
    Vista de análisis por PASILLO.

    Modos:
    - Individual (P1, P2, P3, P4)  → KPIs + tendencia del pasillo seleccionado
    - Comparación (P1–P4)          → una sola gráfica comparativa (elige un KPI)
    - Todos separados              → 4 tarjetas con KPIs + gráfica cada una

    RESPONSABILIDAD:
    - Mostrar datos ya procesados
    - NO calcula
    - NO agrupa
    - NO toca Mongo
    """

    TITLE = "Pasillos"

    MODOS = [
        "Individual",
        "Comparación",
        "Todos separados",
    ]

    PASILLOS_VALIDOS = ["P1", "P2", "P3", "P4"]

    # ─────────────────────────────
    def __init__(self, parent):
        super().__init__(parent)

        # ─────────────────────────
        # Barra superior
        # ─────────────────────────
        top = ttk.Frame(self)
        top.pack(fill="x", pady=6)

        ttk.Label(top, text="Modo:").pack(side="left", padx=5)

        self.modo_var = tk.StringVar(value=self.MODOS[0])
        self.modo_cb = ttk.Combobox(
            top,
            textvariable=self.modo_var,
            values=self.MODOS,
            state="readonly",
            width=18
        )
        self.modo_cb.pack(side="left", padx=5)
        self.modo_var.trace_add("write", lambda *_: self._render_actual())

        ttk.Label(top, text="Pasillo:").pack(side="left", padx=10)

        self.pasillo_var = tk.StringVar()
        self.selector = ttk.Combobox(
            top,
            textvariable=self.pasillo_var,
            state="readonly",
            width=8
        )
        self.selector.pack(side="left")
        self.selector.bind("<<ComboboxSelected>>", lambda _: self._render_actual())

        # ─────────────────────────
        # Selector de KPI para comparación
        # ─────────────────────────
        ttk.Label(top, text="KPI (comparación):").pack(side="left", padx=(18, 5))

        self.kpi_cmp_var = tk.StringVar(value="importe")
        self.kpi_cmp_cb = ttk.Combobox(
            top,
            textvariable=self.kpi_cmp_var,
            values=["importe", "piezas", "devoluciones"],
            state="readonly",
            width=14
        )
        self.kpi_cmp_cb.pack(side="left", padx=5)
        self.kpi_cmp_cb.bind("<<ComboboxSelected>>", lambda _: self._render_actual())

        # ─────────────────────────
        # Contenedor dinámico
        # ─────────────────────────
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Cache
        self._data_por_pasillo = {}
        self._kpis_flags = {}

    # ─────────────────────────
    # Normalización
    # ─────────────────────────
    def _normalizar_pasillo(self, p):
        """
        Convierte:
        - 1,2,3,4 → P1,P2,P3,P4
        - P1,P2,P3,P4 → igual
        Devuelve None si no es válido.
        """
        if p is None:
            return None

        p = str(p).strip().upper()

        if p in self.PASILLOS_VALIDOS:
            return p

        if p.isdigit():
            p2 = f"P{p}"
            if p2 in self.PASILLOS_VALIDOS:
                return p2

        return None

    # ─────────────────────────
    def render(self, resultado: dict) -> None:
        """
        Recibe el resultado completo del ReportesService.
        """
        raw = resultado.get("por_pasillo", {})
        self._kpis_flags = resultado.get("kpis", {})

        # Normalizar y filtrar solo P1–P4
        self._data_por_pasillo = {}
        for key, data in raw.items():
            p = self._normalizar_pasillo(key)
            if not p:
                continue
            self._data_por_pasillo[p] = data

        pasillos = [p for p in self.PASILLOS_VALIDOS if p in self._data_por_pasillo]

        if not pasillos:
            self._limpiar()
            return

        self.selector["values"] = pasillos

        if self.pasillo_var.get() not in pasillos:
            self.pasillo_var.set(pasillos[0])

        # Ajustar KPI comparación a uno válido activo
        self._normalizar_kpi_comparacion()

        self._render_actual()

    # ─────────────────────────
    def _normalizar_kpi_comparacion(self) -> None:
        """
        Asegura que el KPI seleccionado para comparar esté activo en flags.
        Si no, selecciona el primero disponible.
        """
        disponibles = []
        if self._kpis_flags.get("importe"):
            disponibles.append("importe")
        if self._kpis_flags.get("piezas"):
            disponibles.append("piezas")
        if self._kpis_flags.get("devoluciones"):
            disponibles.append("devoluciones")

        if not disponibles:
            self.kpi_cmp_cb.configure(state="disabled")
            self.kpi_cmp_var.set("importe")
            return

        self.kpi_cmp_cb.configure(state="readonly")
        self.kpi_cmp_cb["values"] = disponibles

        if self.kpi_cmp_var.get() not in disponibles:
            self.kpi_cmp_var.set(disponibles[0])

    # ─────────────────────────
    def _render_actual(self) -> None:
        for w in self.container.winfo_children():
            w.destroy()

        modo = self.modo_var.get()

        if modo == "Individual":
            self.selector.configure(state="readonly")
            self.kpi_cmp_cb.configure(state="disabled")
            self._render_individual(self.pasillo_var.get())

        elif modo == "Comparación":
            self.selector.configure(state="disabled")
            # re-habilitar solo si hay kpis disponibles
            self._normalizar_kpi_comparacion()
            if self.kpi_cmp_cb["state"] != "disabled":
                self.kpi_cmp_cb.configure(state="readonly")
            self._render_comparacion()

        elif modo == "Todos separados":
            self.selector.configure(state="disabled")
            self.kpi_cmp_cb.configure(state="disabled")
            self._render_todos()

    # ─────────────────────────
    def _render_individual(self, pasillo: str) -> None:
        data = self._data_por_pasillo.get(pasillo)
        if not data:
            return

        resumen = data.get("resumen", {})
        x = data.get("x")
        y = data.get("y")

        if not x or not y:
            ttk.Label(self.container, text="No hay datos para mostrar.").pack(pady=20)
            return

        # KPIs (3 tarjetas)
        kpi_container = ttk.Frame(self.container)
        kpi_container.pack(fill="x", padx=8, pady=6)

        self._render_kpis_row(kpi_container, resumen)

        # Gráfica
        chart = PlotlyLine()
        chart.update(
            x=x,
            y=y,
            title=f"Tendencia - {pasillo}"
        )

        chart_html = HTMLLabel(self.container, background="white")
        chart_html.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        chart_html.set_html(chart.to_html())

    # ─────────────────────────
    def _render_comparacion(self) -> None:
        """
        Una sola gráfica comparativa entre pasillos.
        Se grafica SOLO el KPI seleccionado (importe/piezas/devoluciones),
        para mantener claridad visual.
        """
        kpi_key = self.kpi_cmp_var.get()

        if not self._kpis_flags.get(kpi_key):
            ttk.Label(
                self.container,
                text="Activa al menos un KPI para comparar."
            ).pack(pady=20)
            return

        # Se espera que cada pasillo traiga x/y ya listos para ese KPI
        # Si tu service aún no separa por KPI, aquí tomamos el mismo x/y
        # (recomendación: en service construir y_cmp por kpi).
        # Formato esperado por pasillo:
        # {
        #   "cmp": {
        #       "importe": {"x":[...], "y":[...]},
        #       "piezas": {"x":[...], "y":[...]},
        #       "devoluciones": {"x":[...], "y":[...]}
        #   }
        # }
        # Si no existe "cmp", caerá a "x/y" genérico.
        series_x = None
        traces = []

        label_map = {
            "importe": "Importe",
            "piezas": "Piezas",
            "devoluciones": "Devoluciones",
        }

        # Construimos una figura multi-línea manual para comparación
        # usando PlotlyLine como base (misma estética), pero agregando varias trazas.
        chart = PlotlyLine(show_legend=True)

        # limpiamos y usaremos self.fig directo (es válido, es UI)
        chart.clear_data()

        for p in self.PASILLOS_VALIDOS:
            d = self._data_por_pasillo.get(p)
            if not d:
                continue

            cmp_block = (d.get("cmp") or {}).get(kpi_key)
            x = (cmp_block or {}).get("x") if cmp_block else None
            y = (cmp_block or {}).get("y") if cmp_block else None

            # fallback
            if not x or not y:
                x = d.get("x")
                y = d.get("y")

            if not x or not y:
                continue

            if series_x is None:
                series_x = x

            # Agregamos traza
            chart.fig.add_trace(
                chart.fig._data_cls.Scatter(  # type: ignore[attr-defined]
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name=f"{p} {label_map.get(kpi_key, kpi_key)}",
                    hovertemplate="<b>%{x}</b><br>Valor: %{y}<extra></extra>"
                )
            )

        if len(chart.fig.data) == 0:
            ttk.Label(self.container, text="No hay datos suficientes para comparar.").pack(pady=20)
            return

        chart.set_title(f"Comparación {label_map.get(kpi_key, kpi_key)} (P1–P4)")

        chart_html = HTMLLabel(self.container, background="white")
        chart_html.pack(fill="both", expand=True, padx=8, pady=8)
        chart_html.set_html(chart.to_html())

    # ─────────────────────────
    def _render_todos(self) -> None:
        grid = ttk.Frame(self.container)
        grid.pack(fill="both", expand=True)

        for i, p in enumerate(self.PASILLOS_VALIDOS):
            data = self._data_por_pasillo.get(p)
            if not data:
                continue

            frame = ttk.LabelFrame(grid, text=f"Pasillo {p}", padding=6)
            frame.grid(
                row=i // 2,
                column=i % 2,
                sticky="nsew",
                padx=6,
                pady=6
            )

            grid.columnconfigure(i % 2, weight=1)
            grid.rowconfigure(i // 2, weight=1)

            resumen = data.get("resumen", {})
            x = data.get("x")
            y = data.get("y")

            if not x or not y:
                continue

            # KPIs
            kpi_container = ttk.Frame(frame)
            kpi_container.pack(fill="x", pady=4)
            self._render_kpis_row(kpi_container, resumen)

            # Gráfica
            chart = PlotlyLine(height=260)
            chart.update(x=x, y=y, title=f"Tendencia - {p}")

            chart_html = HTMLLabel(frame, background="white")
            chart_html.pack(fill="both", expand=True)
            chart_html.set_html(chart.to_html())

    # ─────────────────────────
    def _render_kpis_row(self, parent, resumen: dict) -> None:
        """
        Renderiza una fila de KPIs (Importe / Piezas / Devoluciones) en HTML.
        """
        # Crear renderers por cada KPI visible
        blocks = []

        if self._kpis_flags.get("importe"):
            k = PlotlyKPI(height=170)
            k.update(value=resumen.get("importe", 0), title="Importe", prefix="$")
            blocks.append(k.to_html())

        if self._kpis_flags.get("piezas"):
            k = PlotlyKPI(height=170)
            k.update(value=resumen.get("piezas", 0), title="Piezas")
            blocks.append(k.to_html())

        if self._kpis_flags.get("devoluciones"):
            k = PlotlyKPI(height=170)
            k.update(value=resumen.get("devoluciones", 0), title="Devoluciones")
            blocks.append(k.to_html())

        if not blocks:
            ttk.Label(parent, text="No hay KPIs activos.").pack(pady=10)
            return

        # Render como 1 fila de 3 HTMLLabels
        for html in blocks:
            lbl = HTMLLabel(parent, background="white")
            lbl.pack(side="left", fill="x", expand=True, padx=6)
            lbl.set_html(html)

    # ─────────────────────────
    def _limpiar(self) -> None:
        for w in self.container.winfo_children():
            w.destroy()


