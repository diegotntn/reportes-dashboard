from tkinter import ttk


class Table(ttk.Treeview):
    """
    Tabla genérica basada en Treeview.
    """

    def __init__(self, parent, columns, headings=None, **kwargs):
        super().__init__(
            parent,
            columns=columns,
            show="headings",
            **kwargs
        )

        self.columns_list = columns

        for col in columns:
            self.heading(col, text=headings.get(col, col) if headings else col)
            self.column(col, anchor="center")

    def clear(self):
        for row in self.get_children():
            self.delete(row)

    def load(self, rows):
        self.clear()
        for r in rows:
            self.insert("", "end", values=[r.get(c, "") for c in self.columns_list])

    def selected(self):
        sel = self.selection()
        return self.item(sel[0]) if sel else None
