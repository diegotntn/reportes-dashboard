import plotly.graph_objects as go
from typing import List, Optional, Any

from .base_chart import BasePlotlyChart


class PlotlyLine(BasePlotlyChart):
    """
    PlotlyLine

    Renderer de gráficas de LÍNEAS para el dashboard.

    Este renderer está diseñado para:
    - Mostrar evolución en el tiempo
    - Visualizar tendencias (día, semana, mes)
    - Representar series temporales de manera clara y fluida

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
        smooth: bool = True
    ) -> None:
        """
        Inicializa el renderer de líneas.

        Args:
            theme (str):
                Tema visual ("dark" o "light").

            height (int):
                Altura de la gráfica en píxeles.

            show_legend (bool):
                Indica si se debe mostrar la leyenda.

            smooth (bool):
                Si True, aplica suavizado a la línea
                (curvas tipo dashboard profesional).
        """
        super().__init__(
            theme=theme,
            height=height,
            show_legend=show_legend
        )
        self.smooth = smooth

    # ─────────────────────────────────────────────
    def update(
        self,
        *,
        x: List[Any],
        y: List[float],
        title: Optional[str] = None,
        color: Optional[str] = None
    ) -> None:
        """
        Actualiza la gráfica de líneas con nuevos datos.

        Args:
            x (List[Any]):
                Eje X (fechas, periodos, etiquetas temporales).

            y (List[float]):
                Valores numéricos asociados a cada punto temporal.

            title (Optional[str]):
                Título de la gráfica.

            color (Optional[str]):
                Color de la línea. Si es None, se usa el color
                base definido por el tema.
        """

        # Limpia las trazas previas sin recrear la figura
        self.clear_data()

        line_shape = "spline" if self.smooth else "linear"

        self.fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(
                    shape=line_shape,
                    width=3,
                    color=color or "#22C55E"
                ),
                marker=dict(
                    size=6
                ),
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Valor: %{y}<extra></extra>"
                )
            )
        )

        if title:
            self.set_title(title)

    # ─────────────────────────────────────────────
    def render(self, data: dict) -> None:
        """
        Render inicial del gráfico de líneas.

        Este método permite compatibilidad con el contrato BaseRenderer
        cuando se utiliza el renderer de forma genérica.

        Args:
            data (dict):
                Diccionario con estructura esperada:
                {
                    "x": [...],
                    "y": [...],
                    "title": "..."
                }
        """
        self.update(
            x=data.get("x", []),
            y=data.get("y", []),
            title=data.get("title")
        )

    # ─────────────────────────────────────────────
    def clear(self) -> None:
        """
        Limpia completamente la gráfica de líneas.
        """
        self.clear_data()
