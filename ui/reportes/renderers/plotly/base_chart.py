import plotly.graph_objects as go
from plotly.io import to_html
from typing import Optional, Dict, Any


class BasePlotlyChart:
    """
    BasePlotlyChart

    Este archivo define la BASE VISUAL GLOBAL para TODAS las gráficas Plotly
    del sistema. Funciona como el ADN visual del dashboard y garantiza que
    todas las gráficas compartan:

    - El mismo tema visual (dark / light)
    - Transiciones suaves y consistentes
    - Márgenes y espaciado uniformes
    - Comportamiento homogéneo de animaciones
    - Configuración profesional tipo Power BI / Tableau

    PRINCIPIOS:
    - Aquí NO se manejan datos de negocio.
    - Aquí NO se calculan KPIs.
    - Aquí NO se aplican filtros.
    - Aquí SOLO se define cómo se ve una gráfica.
    """

    def __init__(
        self,
        *,
        theme: str = "dark",
        height: int = 320,
        show_legend: bool = True
    ) -> None:
        """
        Inicializa la figura base de Plotly con configuración global.

        Args:
            theme (str):
                Tema visual de la gráfica.
                Valores soportados:
                - "dark"
                - "light"

            height (int):
                Altura base de la gráfica en píxeles.

            show_legend (bool):
                Indica si la leyenda debe mostrarse por defecto.
        """

        self.fig = go.Figure()

        self._theme = theme
        self._height = height
        self._show_legend = show_legend

        self._apply_base_layout()

    # ─────────────────────────────────────────────
    def _apply_base_layout(self) -> None:
        """
        Aplica el layout base común a todas las gráficas.
        """

        template = "plotly_dark" if self._theme == "dark" else "plotly_white"

        self.fig.update_layout(
            template=template,

            # Tamaño
            height=self._height,

            # Márgenes consistentes
            margin=dict(
                l=32,
                r=32,
                t=48,
                b=32
            ),

            # Animaciones y transiciones suaves
            transition=dict(
                duration=350,
                easing="cubic-in-out"
            ),

            # Leyenda
            showlegend=self._show_legend,

            # Tipografía base
            font=dict(
                family="Segoe UI, Roboto, Arial",
                size=12
            ),

            # Fondo limpio (estilo dashboard)
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            # Comportamiento interactivo
            hovermode="closest"
        )

    # ─────────────────────────────────────────────
    def set_title(self, title: Optional[str]) -> None:
        """
        Define el título de la gráfica.

        Args:
            title (Optional[str]):
                Texto del título. Si es None, se oculta.
        """
        self.fig.update_layout(
            title=dict(
                text=title or "",
                x=0.02,
                xanchor="left",
                font=dict(
                    size=16,
                    weight="bold"
                )
            )
        )

    # ─────────────────────────────────────────────
    def clear_data(self) -> None:
        """
        Elimina todas las trazas de la gráfica.

        Se utiliza antes de actualizar datos para evitar parpadeos
        o residuos visuales.
        """
        self.fig.data = []

    # ─────────────────────────────────────────────
    def update_layout(self, **kwargs: Dict[str, Any]) -> None:
        """
        Permite extender o sobrescribir el layout base de forma controlada.

        Args:
            **kwargs:
                Parámetros adicionales compatibles con update_layout().
        """
        self.fig.update_layout(**kwargs)

    # ─────────────────────────────────────────────
    def to_html(self) -> str:
        """
        Convierte la figura Plotly en HTML embebible.

        Retorna:
            str:
                Fragmento HTML listo para incrustarse en Tkinter,
                WebView o navegador, sin documento completo.
        """
        return to_html(
            self.fig,
            full_html=False,
            include_plotlyjs="cdn",
            config={
                "displaylogo": False,
                "responsive": True,
                "scrollZoom": True
            }
        )

    # ─────────────────────────────────────────────
    def reset(self) -> None:
        """
        Reinicia la gráfica conservando la configuración base.

        Útil cuando se requiere limpiar completamente la visualización
        sin destruir la instancia.
        """
        self.fig = go.Figure()
        self._apply_base_layout()
