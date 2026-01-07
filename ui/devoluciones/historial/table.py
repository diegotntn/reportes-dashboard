import tkinter as tk
from tkinter import ttk
from utils.helpers import money


class HistorialTables(ttk.Frame):
    """
    Tabla del historial de devoluciones.

    RESPONSABILIDAD:
    - Mostrar devoluciones
    - Exponer selección (iid = id real)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    # ─────────────────────────────────────────────
    def _build(self):
        self.devol_tree = ttk.Treeview(
            self,
            columns=("fecha", "folio", "pasillos", "cliente", "motivo", "total"),
            show="headings",
            height=18,
        )

        columnas = [
            ("fecha", "Fecha", 120, "w"),
            ("folio", "Folio", 120, "w"),
            ("pasillos", "Pasillos", 120, "center"),
            ("cliente", "Cliente", 220, "w"),
            ("motivo", "Motivo", 200, "w"),
            ("total", "Total", 110, "e"),
        ]

        for key, title, width, anchor in columnas:
            self.devol_tree.heading(key, text=title)
            self.devol_tree.column(key, width=width, anchor=anchor)

        self.devol_tree.pack(fill="both", expand=True)

    # ─────────────────────────────────────────────
    def clear(self):
        self.devol_tree.delete(*self.devol_tree.get_children())

    # ─────────────────────────────────────────────
    def insert_devolucion(self, row: dict):
        """
        Inserta una devolución en la tabla.

        REGLAS:
        - iid = id real
        - Fecha sin hora
        """

        devolucion_id = row.get("id") or row.get("_id")
        if not devolucion_id:
            return

        fecha = row.get("fecha")
        if fecha:
            fecha = str(fecha)[:10]  # YYYY-MM-DD

        self.devol_tree.insert(
            "",
            tk.END,
            iid=str(devolucion_id),
            values=(
                fecha,
                row.get("folio"),
                row.get("pasillos", "—"),
                row.get("cliente"),
                row.get("motivo"),
                money(row.get("total", 0)),
            ),
        )

    # ─────────────────────────────────────────────
    def selected_devolucion_id(self):
        sel = self.devol_tree.selection()
        return sel[0] if sel else None
