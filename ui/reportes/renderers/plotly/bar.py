import plotly.graph_objects as go
from typing import List, Optional, Any

from .base_chart import BasePlotlyChart


class PlotlyBar(BasePlotlyChart):
    """
    PlotlyBar

    Renderer de gráficas de BARRAS para el dashboard.

    Este renderer se utiliza para:
    - Comparaciones entre categorías (pasillos, zonas, personas, etc.)
    - Visualización clara de totales o métricas comparables
    - Dashboards estilo Power BI / Tableau

    PRINCIPIOS:
    - NO realiza cálculos.
    - NO agrupa datos.
    - NO conoce filtros ni lógica de negocio.
    - SOLO recibe datos ya procesados y listos para mostrar.
    """

    def __init__(
        self,
        *,
        theme: str = "dark",
        height: int = 320,
        show_legend: bool = False,
        orientation: str = "v"
    ) -> None:
        """
        Inicializa el renderer de barras.

        Args:
            theme (str):
                Tema visual ("dark" o "light").

            height (int):
                Altura de la gráfica en píxeles.

            show_legend (bool):
                Indica si se debe mostrar la leyenda.

            orientation (str):
                Orientación de las barras:
                - "v" → vertical
                - "h" → horizontal
        """
        super().__init__(
            theme=theme,
            height=height,
            show_legend=show_legend
        )
        self.orientation = orientation

    # ─────────────────────────────────────────────
    def update(
        self,
        *,
        labels: List[Any],
        values: List[float],
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> None:
        """
        Actualiza la gráfica de barras con nuevos datos.

        Args:
            labels (List[Any]):
                Etiquetas del eje categórico
                (ej. pasillos, zonas).

            values (List[float]):
                Valores numéricos asociados a cada etiqueta.

            title (Optional[str]):
                Título de la gráfica.

            color (Optional[str]):
                Color de las barras. Si es None, se usa el color
                base definido por el tema.
        """

        # Limpia las trazas previas sin recrear la figura
        self.clear_data()

        bar_args = {
            "x": labels,
            "y": values,
            "marker": {
                "color": color or "#2563EB",
                "line": {"width": 0}
            },
            "hovertemplate": (
                "<b>%{x}</b><br>"
                "Valor: %{y}<extra></extra>"
            )
        }

        # Soporte para barras horizontales
        if self.orientation == "h":
            bar_args["x"], bar_args["y"] = values, labels
            bar_args["orientation"] = "h"
            bar_args["hovertemplate"] = (
                "<b>%{y}</b><br>"
                "Valor: %{x}<extra></extra>"
            )

        self.fig.add_trace(go.Bar(**bar_args))

        if title:
            self.set_title(title)

    # ─────────────────────────────────────────────
    def render(self, data: dict) -> None:
        """
        Render inicial del gráfico de barras.

        Este método permite compatibilidad con el contrato BaseRenderer
        cuando se utiliza el renderer de forma genérica.

        Args:
            data (dict):
                Diccionario con estructura esperada:
                {
                    "labels": [...],
                    "values": [...],
                    "title": "..."
                }
        """
        self.update(
            labels=data.get("labels", []),
            values=data.get("values", []),
            title=data.get("title")
        )

    # ─────────────────────────────────────────────
    def clear(self) -> None:
        """
        Limpia completamente la gráfica de barras.
        """
        self.clear_data()
