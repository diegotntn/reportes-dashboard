import tkinter as tk
from tkinter import ttk


class PrimaryButton(ttk.Button):
    """Botón principal (acciones afirmativas)"""

    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            style="Primary.TButton",
            **kwargs
        )


class DangerButton(ttk.Button):
    """Botón de acciones destructivas"""

    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            style="Danger.TButton",
            **kwargs
        )


class SecondaryButton(ttk.Button):
    """Botón secundario"""

    def __init__(self, parent, text, command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            **kwargs
        )
