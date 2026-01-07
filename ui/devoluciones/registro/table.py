from tkinter import ttk
from utils.helpers import money


class ArticulosTable(ttk.LabelFrame):
    """
    Tabla de artículos devueltos.
    """

    def __init__(self, parent):
        super().__init__(parent, text="Artículos devueltos", padding=10)

        self._items = []

        columnas = (
            "codigo",
            "nombre",
            "pasillo",
            "cantidad",
            "unitario",
            "total",
        )

        self.tree = ttk.Treeview(
            self,
            columns=columnas,
            show="headings",
            height=8
        )

        headings = {
            "codigo": "Código",
            "nombre": "Nombre",
            "pasillo": "Pasillo",
            "cantidad": "Cant",
            "unitario": "Unit",
            "total": "Total",
        }

        for col, txt in headings.items():
            self.tree.heading(col, text=txt)
            self.tree.column(col, anchor="center")

        self.tree.pack(fill="both", expand=True)

    # ─────────────────────────────
    # API USADA POR EVENTS
    # ─────────────────────────────
    def add_item(
        self,
        *,
        clave: str,
        descripcion: str,
        cantidad: int,
        precio: float,
        pasillo: str
    ):
        """
        Agrega un artículo a la tabla y al buffer interno.
        """
        total = cantidad * precio

        item = {
            "clave": clave,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio": precio,
            "pasillo": pasillo,
            "total": total,
        }

        self._items.append(item)

        self.tree.insert(
            "",
            "end",
            values=(
                clave,
                descripcion,
                pasillo,
                cantidad,
                money(precio),
                money(total),
            )
        )

    def get_items(self):
        """
        Devuelve los artículos listos para guardar.
        """
        return list(self._items)

    def clear(self):
        """
        Limpia la tabla y el buffer.
        """
        self._items.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)
