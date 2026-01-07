from tkinter import ttk
from datetime import date
from tkcalendar import DateEntry

from utils.helpers import first_day_month


class HistorialFilters(ttk.LabelFrame):
    """
    Filtros de fecha para el historial de devoluciones.

    Responsabilidades:
    - Mostrar DateEntry Desde / Hasta
    - Validar rango de fechas
    - Proveer filtros normalizados a la capa Events
    """

    def __init__(self, parent):
        super().__init__(parent, text="Filtro por fecha (historial)", padding=10)

        # ───── Widgets ─────
        self.desde_entry = DateEntry(
            self,
            date_pattern="yyyy-mm-dd"
        )

        self.hasta_entry = DateEntry(
            self,
            date_pattern="yyyy-mm-dd"
        )

        # ───── Valores por defecto ─────
        self.desde_entry.set_date(first_day_month(date.today()))
        self.hasta_entry.set_date(date.today())

        self._layout()

    # ─────────────────────────────
    def _layout(self):
        ttk.Label(self, text="Desde").grid(row=0, column=0, sticky="w")
        self.desde_entry.grid(row=1, column=0, padx=(0, 16))

        ttk.Label(self, text="Hasta").grid(row=0, column=1, sticky="w")
        self.hasta_entry.grid(row=1, column=1, padx=(0, 16))

    # ─────────────────────────────
    def get_filtros(self) -> dict:
        """
        Devuelve filtros listos para Events / Service.
        """
        desde = self.desde_entry.get_date()
        hasta = self.hasta_entry.get_date()

        if hasta < desde:
            raise ValueError("El rango de fechas no es válido.")

        return {
            "desde": desde,
            "hasta": hasta,
        }

    # ─────────────────────────────
    def get_range(self):
        """
        Método de compatibilidad (si ya se usa en otro lugar).
        """
        filtros = self.get_filtros()
        return filtros["desde"], filtros["hasta"]
