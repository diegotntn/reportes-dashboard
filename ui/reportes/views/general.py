from tkinter import ttk

from ui.reportes.renderers.plotly import PlotlyKPI, PlotlyLine


class GeneralView(ttk.Frame):
    """
    Vista General de Reportes.

    RESPONSABILIDAD:
    - Mostrar KPIs globales
    - Mostrar tendencia general en el tiempo
    - Renderiza en WebView global (pywebview)
    """

    TITLE = "General"

    def __init__(self, parent):
        super().__init__(parent)

        # Renderers Plotly (NO WebView aquí)
        self.kpi_importe = PlotlyKPI()
        self.kpi_piezas = PlotlyKPI()
        self.kpi_devoluciones = PlotlyKPI()
        self.chart = PlotlyLine()

    # ─────────────────────────
    def render(self, data: dict) -> None:
        if not data:
            return

        kpis_flags = data.get("kpis", {})
        resumen = data.get("resumen", {})
        general = data.get("general")

        # ───── KPIs ─────
        kpi_blocks = []

        if kpis_flags.get("importe"):
            self.kpi_importe.update(
                value=resumen.get("importe_total", 0),
                title="Importe",
                prefix="$"
            )
            kpi_blocks.append(self.kpi_importe.to_html())

        if kpis_flags.get("piezas"):
            self.kpi_piezas.update(
                value=resumen.get("piezas_total", 0),
                title="Piezas"
            )
            kpi_blocks.append(self.kpi_piezas.to_html())

        if kpis_flags.get("devoluciones"):
            self.kpi_devoluciones.update(
                value=resumen.get("devoluciones_total", 0),
                title="Devoluciones"
            )
            kpi_blocks.append(self.kpi_devoluciones.to_html())

        # ───── Gráfica ─────
        chart_html = ""
        if general:
            x = general.get("x")
            y = general.get("y")
            if x and y:
                self.chart.update(
                    x=x,
                    y=y,
                    title="Tendencia general"
                )
                chart_html = self.chart.to_html()

        # ───── HTML final ─────
        html = self._build_dashboard_html(
            kpis_html=kpi_blocks,
            chart_html=chart_html
        )

        # 🔥 USAR WEBVIEW GLOBAL
        self.winfo_toplevel().web_renderer.set_html(html)

    # ─────────────────────────
    def _build_dashboard_html(self, kpis_html, chart_html) -> str:
        kpis_row = "".join(
            f'<div class="kpi">{h}</div>' for h in kpis_html
        )

        return f"""
        <html>
        <head>
            <meta charset="utf-8"/>
            <style>
                body {{
                    margin: 0;
                    padding: 16px;
                    font-family: Segoe UI, Roboto, Arial;
                    background: #0F172A;
                    color: #E5E7EB;
                }}
                .kpis {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                }}
                .kpi {{
                    background: #020617;
                    border-radius: 8px;
                    padding: 8px;
                }}
                .chart {{
                    background: #020617;
                    border-radius: 8px;
                    padding: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="kpis">
                {kpis_row}
            </div>
            <div class="chart">
                {chart_html}
            </div>
        </body>
        </html>
        """
