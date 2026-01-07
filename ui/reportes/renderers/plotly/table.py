import plotly.graph_objects as go
from plotly.io import to_html
from typing import List, Any, Optional


class PlotlyTable:
    """
    PlotlyTable

    Renderer de TABLAS INTERACTIVAS usando Plotly.

    Este renderer se utiliza para:
    - Mostrar tablas de resumen
    - Tablas comparativas (por pasillo, zona, persona)
    - Información tabular con estilo tipo Power BI / Tableau

    CARACTERÍSTICAS VISUALES:
    - Hover por fila
    - Scroll automático
    - Encabezados fijos
    - Estilo limpio y profesional

    PRINCIPIOS:
    - NO realiza cálculos.
    - NO transforma datos.
    - NO accede a servicios ni bases de datos.
    - SOLO recibe datos ya procesados y listos para mostrar.
    """

    def __init__(
        self,
        *,
        theme: str = "dark",
        height: int = 320
    ) -> None:
        """
        Inicializa la tabla interactiva.

        Args:
            theme (str):
                Tema visual ("dark" o "light").

            height (int):
                Altura de la tabla en píxeles.
        """
        self.theme = theme
        self.height = height
        self.fig = go.Figure()

        self._apply_base_layout()

    # ─────────────────────────────────────────────
    def _apply_base_layout(self) -> None:
        """
        Aplica el layout base visual de la tabla.
        """
        template = "plotly_dark" if self.theme == "dark" else "plotly_white"

        self.fig.update_layout(
            template=template,
            height=self.height,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Segoe UI, Roboto, Arial",
                size=12
            )
        )

    # ─────────────────────────────────────────────
    def update(
        self,
        *,
        headers: List[str],
        rows: List[List[Any]],
        column_widths: Optional[List[int]] = None
    ) -> None:
        """
        Actualiza la tabla con nuevos datos.

        Args:
            headers (List[str]):
                Lista de encabezados de columna.

            rows (List[List[Any]]):
                Datos de la tabla organizados por columnas
                (formato requerido por Plotly Table).

            column_widths (Optional[List[int]]):
                Anchos personalizados de columnas.
        """

        self.fig.data = []

        self.fig.add_trace(
            go.Table(
                header=dict(
                    values=headers,
                    fill_color="#1F2937",
                    font=dict(size=12, color="white"),
                    align="left",
                    height=28
                ),
                cells=dict(
                    values=rows,
                    fill_color="#111827",
                    font=dict(size=11, color="white"),
                    align="left",
                    height=24
                ),
                columnwidth=column_widths
            )
        )

    # ─────────────────────────────────────────────
    def render(self, data: dict) -> None:
        """
        Render inicial de la tabla (compatible con contrato genérico).

        Args:
            data (dict):
                Estructura esperada:
                {
                    "headers": [...],
                    "rows": [...],
                    "column_widths": [...]
                }
        """
        self.update(
            headers=data.get("headers", []),
            rows=data.get("rows", []),
            column_widths=data.get("column_widths")
        )

    # ─────────────────────────────────────────────
    def clear(self) -> None:
        """
        Limpia completamente la tabla.
        """
        self.fig.data = []

    # ─────────────────────────────────────────────
    def to_html(self) -> str:
        """
        Convierte la tabla en HTML embebible.

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
