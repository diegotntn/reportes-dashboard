from tkinter import ttk


class BaseForm(ttk.Frame):
    """
    Formulario base reutilizable.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.fields = {}

    def get_data(self):
        """
        Devuelve dict con valores del formulario.
        """
        return {
            k: v.get()
            for k, v in self.fields.items()
        }

    def set_data(self, data: dict):
        """
        Carga valores al formulario.
        """
        for k, v in data.items():
            if k in self.fields:
                self.fields[k].set(v)

    def clear(self):
        for v in self.fields.values():
            v.set("")
