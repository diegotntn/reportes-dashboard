from tkinter import ttk

from .form import PersonalForm
from .table import PersonalTables
from .events import PersonalEvents


class PersonalScreen(ttk.Frame):
    """
    Contenedor principal de gestión de personal operativo y asignaciones.
    """

    def __init__(self, parent, personal_service):
        super().__init__(parent)

        self.events = PersonalEvents(personal_service)

    def build(self):
        cont = ttk.Frame(self, padding=12)
        cont.pack(fill="both", expand=True)

        self.form = PersonalForm(cont)
        self.form.pack(fill="x")

        self.tables = PersonalTables(cont)
        self.tables.pack(fill="both", expand=True, pady=(10, 0))

        self.events.bind(self.form, self.tables)
        self.events.refresh_all()
