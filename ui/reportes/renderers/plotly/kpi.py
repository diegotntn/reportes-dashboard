import plotly.graph_objects as go
from plotly.io import to_html
from typing import Optional


class PlotlyKPI:
    """
    PlotlyKPI

    Renderer de KPI Cards estilo Power BI / Tableau.

    Este renderer está diseñado para mostrar indicadores clave de forma:
    - Clara
    - Grande
    - Visualmente impactante
    - Con animación automática de cambio (delta)

    Se utiliza principalmente en:
    - Vista General
    - Encabezados de dashboards
    - Resúmenes ejecutivos

    PRINCIPIOS:
    - NO calcula valores.
    - NO compara periodos.
    - NO accede a datos.
    - SOLO recibe valores finales ya procesados.
    """

    def __init__(
        self,
        *,
        theme: str = "dark",
        height: int = 180
    ) -> None:
        """
        Inicializa la tarjeta KPI.

        Args:
            theme (str):
                Tema visual ("dark" o "light").

            height (int):
                Altura de la tarjeta KPI.
        """
        self.theme = theme
        self.height = height
        self.fig = go.Figure()

        self._apply_base_layout()

    # ─────────────────────────────────────────────
    def _apply_base_layout(self) -> None:
        """
        Aplica el layout base visual del KPI.
        """
        template = "plotly_dark" if self.theme == "dark" else "plotly_white"

        self.fig.update_layout(
            template=template,
            height=self.height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Segoe UI, Roboto, Arial",
                size=14
            )
        )

    # ─────────────────────────────────────────────
    def update(
        self,
        *,
        value: float,
        previous: Optional[float] = None,
        title: str = "",
        prefix: str = "",
        suffix: str = ""
    ) -> None:
        """
        Actualiza el KPI con un nuevo valor.

        Args:
            value (float):
                Valor actual del indicador.

            previous (Optional[float]):
                Valor de referencia para calcular el delta.
                Si es None, no se muestra delta.

            title (str):
                Título del KPI.

            prefix (str):
                Prefijo del valor (ej. "$").

            suffix (str):
                Sufijo del valor (ej. "%").
        """

        self.fig.data = []

        indicator_args = dict(
            mode="number+delta" if previous is not None else "number",
            value=value,
            title={
                "text": title,
                "font": {"size": 14}
            },
            number={
                "font": {"size": 42},
                "prefix": prefix,
                "suffix": suffix
            }
        )

        if previous is not None:
            indicator_args["delta"] = {
                "reference": previous,
                "relative": True,
                "valueformat": ".1%",
                "increasing": {"color": "#22C55E"},
                "decreasing": {"color": "#EF4444"}
            }

        self.fig.add_trace(go.Indicator(**indicator_args))

    # ─────────────────────────────────────────────
    def render(self, data: dict) -> None:
        """
        Render inicial del KPI (compatible con contrato genérico).

        Args:
            data (dict):
                Estructura esperada:
                {
                    "value": 120,
                    "previous": 100,
                    "title": "Total devoluciones",
                    "prefix": "$",
                    "suffix": ""
                }
        """
        self.update(
            value=data.get("value", 0),
            previous=data.get("previous"),
            title=data.get("title", ""),
            prefix=data.get("prefix", ""),
            suffix=data.get("suffix", "")
        )

    # ─────────────────────────────────────────────
    def clear(self) -> None:
        """
        Limpia el KPI.
        """
        self.fig.data = []

    # ─────────────────────────────────────────────
    def to_html(self) -> str:
        """
        Convierte el KPI en HTML embebible.

        Retorna:
            str:
                Fragmento HTML listo para incrustarse en Tkinter
                o WebView.
        """
        return to_html(
            self.fig,
            full_html=False,
            include_plotlyjs="cdn",
            config={
                "displaylogo": False,
                "responsive": True
            }
        )
