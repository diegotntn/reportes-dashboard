import tkinter as tk
from tkinter import ttk


# ─────────────────────────────────────────────
# Diálogo base
# ─────────────────────────────────────────────
class BaseDialog(tk.Toplevel):
    """
    Diálogo base reutilizable para toda la aplicación.

    RESPONSABILIDADES:
    - Crear ventana modal (Toplevel)
    - Manejar grab_set / grab_release
    - Proveer contenedor estándar (self.container)

    NO conoce:
    - Services
    - DB
    - Dominio
    """

    def __init__(
        self,
        parent,
        title: str = "Diálogo",
        modal: bool = True,
        resizable: bool = False,
        geometry: str | None = None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.title(title)
        self.resizable(resizable, resizable)
        self.transient(parent)

        if geometry:
            self.geometry(geometry)

        if modal:
            self.grab_set()

        # Contenedor raíz común
        self.container = ttk.Frame(self, padding=12)
        self.container.pack(fill="both", expand=True)

        # Cierre limpio
        self.protocol("WM_DELETE_WINDOW", self.close)

    # ─────────────────────────
    def close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()


# ─────────────────────────────────────────────
# Diálogo de confirmación
# ─────────────────────────────────────────────
class ConfirmDialog(BaseDialog):
    """
    Diálogo de confirmación genérico.

    Uso:
        ConfirmDialog(
            parent,
            message="¿Seguro?",
            on_confirm=callback
        )
    """

    def __init__(
        self,
        parent,
        message: str,
        on_confirm,
        title: str = "Confirmar",
    ):
        super().__init__(
            parent,
            title=title,
            modal=True,
            resizable=False,
            geometry="360x160"
        )

        ttk.Label(
            self.container,
            text=message,
            wraplength=320,
            justify="left"
        ).pack(pady=(0, 16))

        btns = ttk.Frame(self.container)
        btns.pack(fill="x")

        ttk.Button(
            btns,
            text="Cancelar",
            command=self.close
        ).pack(side="right", padx=6)

        ttk.Button(
            btns,
            text="Aceptar",
            command=lambda: self._confirm(on_confirm)
        ).pack(side="right")

    def _confirm(self, callback):
        if callable(callback):
            callback()
        self.close()


# ─────────────────────────────────────────────
# Diálogo de error simple (opcional pero útil)
# ─────────────────────────────────────────────
class ErrorDialog(BaseDialog):
    """
    Diálogo de error genérico.
    Evita repetir messagebox.showerror en toda la UI.
    """

    def __init__(
        self,
        parent,
        message: str,
        title: str = "Error",
    ):
        super().__init__(
            parent,
            title=title,
            modal=True,
            resizable=False,
            geometry="380x180"
        )

        ttk.Label(
            self.container,
            text=message,
            wraplength=340,
            foreground="red",
            justify="left"
        ).pack(pady=(0, 20))

        ttk.Button(
            self.container,
            text="Cerrar",
            command=self.close
        ).pack()
