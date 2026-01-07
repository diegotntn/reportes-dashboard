from tkinter import ttk
from datetime import date

from ui.reportes.controller import ReportesController
from ui.reportes.filters.panel import FiltersPanel

from ui.reportes.views.general import GeneralView
from ui.reportes.views.zonas import ZonasView
from ui.reportes.views.pasillos import PasillosView
from ui.reportes.views.personas import PersonasView
from ui.reportes.views.detalle import DetalleView


class ReportesScreen(ttk.Frame):
    """
    Pantalla principal de Reportes.

    RESPONSABILIDADES:
    - Mostrar panel de filtros
    - Contener vistas (Notebook)
    - Orquestar actualización SINCRONA vía controller
    - Delegar renderizado a cada vista

    REGLAS:
    - NO lógica de negocio
    - NO Mongo
    - NO pandas
    - NO threads
    """

    def __init__(self, parent, reportes_service):
        super().__init__(parent)

        # ─────────────────────────
        # Service
        # ─────────────────────────
        self.reportes_service = reportes_service

        # ─────────────────────────
        # Controller (SINCRONO)
        # ─────────────────────────
        self.controller = ReportesController(
            service=self.reportes_service,
            on_result=self._render
        )

        # Flag para evitar renders duplicados
        self._render_inicial_hecho = False

        # ─────────────────────────
        # UI
        # ─────────────────────────
        self._build()

    # ─────────────────────────────
    def _build(self) -> None:
        """
        Construye panel de filtros + notebook de vistas.
        """

        # ───── Panel de filtros (ARRIBA) ─────
        self.filters = FiltersPanel(
            self,
            on_change=self.actualizar
        )
        self.filters.pack(fill="x", padx=10, pady=(8, 4))

        # ───── Notebook de vistas ─────
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # ORDEN DEFINITIVO DE VISTAS
        self.views = [
            GeneralView(self.notebook),
            PasillosView(self.notebook),
            PersonasView(self.notebook),
            ZonasView(self.notebook),
            DetalleView(self.notebook),
        ]

        for view in self.views:
            self.notebook.add(view, text=view.TITLE)

    # ─────────────────────────────
    def actualizar(self, filtros=None):
        """
        Dispara la generación de reportes.

        - Puede ser llamado:
          * al entrar a la pestaña
          * al cambiar filtros
        """
        print("🟡 ReportesScreen.actualizar() llamado")

        if filtros is None:
            filtros = self._filtros_por_defecto()

        print("🟡 Filtros usados:", filtros)

        self.controller.actualizar(filtros)

    # ─────────────────────────────
    def _filtros_por_defecto(self) -> dict:
        """
        Filtros iniciales por defecto (mes actual).
        """
        hoy = date.today()
        return {
            "desde": hoy.replace(day=1).isoformat(),
            "hasta": hoy.isoformat(),
        }

    # ─────────────────────────────
    def _render(self, resultado: dict) -> None:
        """
        Renderiza resultados en todas las vistas.
        """
        print("🟣 ReportesScreen._render() llamado")

        if not resultado:
            print("⚠️ Resultado vacío, no se renderiza")
            return

        for view in self.views:
            view.render(resultado)

        self._render_inicial_hecho = True
