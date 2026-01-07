import plotly.graph_objects as go
from typing import List, Optional, Any

from .base_chart import BasePlotlyChart


class PlotlyPie(BasePlotlyChart):
    """
    PlotlyPie

    Renderer de gráficas PIE / DONUT para el dashboard.

    Este renderer se utiliza para:
    - Mostrar participación porcentual por categoría
    - Comparar distribución entre pasillos, zonas u otras dimensiones
    - Visualizaciones compactas y claras tipo Power BI / Tableau

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
        show_legend: bool = True,
        donut: bool = True
    ) -> None:
        """
        Inicializa el renderer de pie / donut.

        Args:
            theme (str):
                Tema visual ("dark" o "light").

            height (int):
                Altura de la gráfica en píxeles.

            show_legend (bool):
                Indica si se debe mostrar la leyenda.

            donut (bool):
                Si True, renderiza una gráfica tipo donut.
                Si False, renderiza una gráfica pie tradicional.
        """
        super().__init__(
            theme=theme,
            height=height,
            show_legend=show_legend
        )
        self.donut = donut

    # ─────────────────────────────────────────────
    def update(
        self,
        *,
        labels: List[Any],
        values: List[float],
        title: Optional[str] = None,
        colors: Optional[List[str]] = None
    ) -> None:
        """
        Actualiza la gráfica pie / donut con nuevos datos.

        Args:
            labels (List[Any]):
                Etiquetas de cada segmento
                (ej. pasillos, zonas).

            values (List[float]):
                Valores numéricos asociados a cada etiqueta.

            title (Optional[str]):
                Título de la gráfica.

            colors (Optional[List[str]]):
                Lista de colores personalizados para los segmentos.
                Si es None, Plotly utiliza la paleta por defecto.
        """

        # Limpia las trazas previas sin recrear la figura
        self.clear_data()

        self.fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4 if self.donut else 0.0,
                marker=dict(
                    colors=colors
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Valor: %{value}<br>"
                    "Porcentaje: %{percent}<extra></extra>"
                ),
                textinfo="percent",
                textfont=dict(size=12)
            )
        )

        if title:
            self.set_title(title)

    # ─────────────────────────────────────────────
    def render(self, data: dict) -> None:
        """
        Render inicial del gráfico pie / donut.

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
        Limpia completamente la gráfica pie / donut.
        """
        self.clear_data()
