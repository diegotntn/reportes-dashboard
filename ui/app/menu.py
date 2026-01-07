from tkinter import ttk

# ───────── UI Screens ─────────
from ui.devoluciones.registro.screen import RegistroScreen
from ui.devoluciones.historial.screen import HistorialScreen
from ui.reportes.screen import ReportesScreen
from ui.personal.screen import PersonalScreen


class AppMenu(ttk.Notebook):
    """
    Menú principal de pestañas (Notebook).

    RESPONSABILIDADES:
    - Crear y registrar pantallas (screens)
    - Inyectar services y estado
    - Disparar Reportes SOLO al entrar a la pestaña
    """

    def __init__(self, parent, *, servicios, state):
        super().__init__(parent)

        self.servicios = servicios
        self.state = state

        # Flag para evitar renders duplicados
        self._reportes_renderizado = False

        self._crear_tabs()

        # 🔥 Escuchar cambio de pestaña
        self.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # ─────────────────────────────
    def _crear_tabs(self):
        """Crea y registra las pestañas del sistema."""

        # ───── Registro ─────
        self.registro = RegistroScreen(
            parent=self,
            devoluciones_service=self.servicios["devoluciones"],
            productos_service=self.servicios["productos"],
            on_saved=self.state.notify_data_change
        )
        self.add(self.registro, text="Registro")

        # ───── Reportes ─────
        self.reportes = ReportesScreen(
            parent=self,
            reportes_service=self.servicios["reportes"]
        )
        self.add(self.reportes, text="Reportes")

        # ───── Historial ─────
        self.historial = HistorialScreen(
            parent=self,
            devoluciones_service=self.servicios["devoluciones"],
            on_change=self.state.notify_data_change
        )
        self.add(self.historial, text="Historial")

        # ───── Personal ─────
        self.personal = PersonalScreen(
            parent=self,
            personal_service=self.servicios["personal"]
        )
        self.add(self.personal, text="Personal")

    # ─────────────────────────────
    def inicializar(self):
        """
        Inicialización inicial de la UI.
        Se llama UNA sola vez desde MainWindow.

        REGLAS:
        - NO disparar reportes aquí
        - NO lógica pesada
        """

        # Estas pantallas requieren build explícito
        self.registro.build()
        self.personal.build()

        # Historial y Reportes se manejan por eventos

    # ─────────────────────────────
    def _on_tab_changed(self, event):
        """
        Maneja el cambio de pestaña.
        Reportes se renderiza SOLO al entrar por primera vez.
        """
        selected = event.widget.select()
        tab_text = event.widget.tab(selected, "text")

        print("📌 Pestaña seleccionada:", tab_text)

        if tab_text == "Reportes":
            if not self._reportes_renderizado:
                print("🚀 Disparando render inicial de Reportes")
                self._reportes_renderizado = True
                self.reportes.actualizar()
            else:
                print("ℹ️ Reportes ya renderizado, no se repite")

        # Historial NO se construye aquí (ya maneja su lógica interna)
