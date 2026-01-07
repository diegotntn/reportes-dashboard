import tkinter as tk

# ───────── Base de datos (infraestructura) ─────────
from db import get_db

# ───────── Repositorios ─────────
from db.mongo.repos.productos_repo import ProductosRepo

# ───────── Adapters (queries Mongo) ─────────
from db.mongo.reportes.queries import ReportesQueries

# ───────── Services (fachadas) ─────────
from services.devoluciones.facade import DevolucionesService
from services.productos_service import ProductosService
from services.personal_service import PersonalService
from services.reportes import ReportesService

# ───────── UI Core ─────────
from ui.app.menu import AppMenu
from ui.app.state import AppState


class MainWindow(tk.Tk):
    """
    Ventana principal de la aplicación.

    RESPONSABILIDADES:
    - Crear infraestructura (DB Provider)
    - Crear repositorios
    - Crear queries (lectura especializada)
    - Crear services correctamente inyectados
    - Registrar servicios en un solo diccionario
    - Inyectar infraestructura global (WebView)
    - Inicializar UI y estado global

    REGLA:
    - MainWindow NO dispara reportes
    - MainWindow NO llama controllers
    """

    def __init__(self, *, web_renderer):
        super().__init__()

        # ───────────────── Ventana ─────────────────
        self.title("Sistema de Devoluciones")
        self.geometry("1250x760")
        self.minsize(1100, 680)

        # ───────────────── Infraestructura GLOBAL ─────────────────
        self.web_renderer = web_renderer

        # ───────────────── Infraestructura DB ─────────────────
        self.db_provider = get_db()

        # ───────────────── Repositorios ─────────────────
        self.productos_repo = ProductosRepo(self.db_provider._db)

        # ───────────────── Queries ─────────────────
        self.reportes_queries = ReportesQueries(self.db_provider)

        # ───────────────── Services ─────────────────
        self.productos_service = ProductosService(self.productos_repo)
        self.personal_service = PersonalService(self.db_provider)

        self.devoluciones_service = DevolucionesService(
            db=self.db_provider,
            reportes_queries=self.reportes_queries
        )

        self.reportes_service = ReportesService(
            reportes_queries=self.reportes_queries,
            personal_service=self.personal_service
        )

        # ───────────────── Registro de servicios ─────────────────
        self.servicios = {
            "productos": self.productos_service,
            "devoluciones": self.devoluciones_service,
            "personal": self.personal_service,
            "reportes": self.reportes_service,
        }

        # ───────────────── Estado global ─────────────────
        self.state = AppState()

        # ───────────────── Menú principal ─────────────────
        self.menu = AppMenu(
            parent=self,
            servicios=self.servicios,
            state=self.state
        )
        self.menu.pack(fill="both", expand=True)

        # ───────────────── Suscripciones ─────────────────
        self.state.subscribe_data_change(self._on_data_change)

        # ───────────────── Inicialización UI ─────────────────
        self.menu.inicializar()

        # ───────────────── Cierre limpio ─────────────────
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ─────────────────────────────────────────────
    def _on_data_change(self):
        """
        Callback global cuando cambian datos.

        REGLA:
        - NO refrescar Reportes automáticamente aquí (evita renders fantasma)
        - Historial sí puede refrescar porque es UI interna (Tk) y ligera
        """
        if hasattr(self.menu, "historial"):
            self.menu.historial.events.cargar_historial()

    # ─────────────────────────────────────────────
    def on_close(self):
        """
        Cierre limpio de la aplicación.
        """
        try:
            if hasattr(self.db_provider, "close"):
                self.db_provider.close()
        finally:
            self.destroy()
