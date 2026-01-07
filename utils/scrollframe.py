import tkinter as tk
from tkinter import ttk


class ScrollFrame(ttk.Frame):
    """
    Frame con scroll vertical reutilizable y seguro.
    Evita scroll negativo y espacios en blanco.
    """

    def __init__(self, master):
        super().__init__(master)

        # Canvas + Scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.v_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scroll.pack(side="right", fill="y")

        # Frame interno
        self.inner = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )

        # Ajustes automáticos
        self.inner.bind("<Configure>", self._on_inner_configure)
        self.canvas.bind("<Configure>", self._resize_inner)

        # Scroll con rueda del mouse
        self._bind_mousewheel()

        # Alias por compatibilidad
        self.frame = self.inner

    # ───────────────────────── CONFIGURACIONES ─────────────────────────

    def _on_inner_configure(self, _):
        """Actualiza región de scroll y corrige límites"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._clamp_scroll()

    def _resize_inner(self, event):
        """Ajusta ancho del frame interno al canvas"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._clamp_scroll()

    # ───────────────────────── SCROLL ─────────────────────────

    def _bind_mousewheel(self):
        # Windows / macOS
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _on_mousewheel(self, event):
        if not self._scroll_needed():
            return

        delta = int(-1 * (event.delta / 120))
        self.canvas.yview_scroll(delta, "units")
        self._clamp_scroll()

    def _on_mousewheel_linux(self, event):
        if not self._scroll_needed():
            return

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

        self._clamp_scroll()

    # ───────────────────────── SEGURIDAD ─────────────────────────

    def _scroll_needed(self):
        """Evita scroll si el contenido no excede el canvas"""
        bbox = self.canvas.bbox("all")
        if not bbox:
            return False

        content_height = bbox[3] - bbox[1]
        canvas_height = self.canvas.winfo_height()

        return content_height > canvas_height

    def _clamp_scroll(self):
        """Evita scroll fuera de rango (espacios en blanco)"""
        first, last = self.canvas.yview()

        if first < 0:
            self.canvas.yview_moveto(0)

        if last > 1:
            self.canvas.yview_moveto(1)
