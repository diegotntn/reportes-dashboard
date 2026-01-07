import tkinter as tk
from tkinter import ttk, messagebox

from utils.constants import PASILLOS
from utils.helpers import money, fint, ffloat


class EditArticulosTable(ttk.LabelFrame):
    """
    Tabla de artículos con edición inline.

    RESPONSABILIDAD:
    - Mostrar artículos
    - Permitir edición de pasillo, cantidad y unitario
    - Mantener totales actualizados
    - Exponer datos listos para guardar
    - Detectar si el usuario modificó artículos
    """

    def __init__(self, parent, arts_df):
        super().__init__(
            parent,
            text="Artículos (doble clic para editar)",
            padding=10,
        )

        # ─────────────────────────────────────────────
        # Estado interno
        # ─────────────────────────────────────────────
        self.items = []
        self._dirty = False   # 👈 CLAVE: cambios del usuario

        # ─────────────────────────────────────────────
        # Layout
        # ─────────────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ─────────────────────────────────────────────
        # Treeview
        # ─────────────────────────────────────────────
        self.tree = ttk.Treeview(
            self,
            columns=("nombre", "codigo", "pasillo", "cantidad", "unitario", "total", "id"),
            show="headings",
            selectmode="browse",
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self._on_double_click)

        columns = [
            ("nombre", "Nombre", 260, True),
            ("codigo", "Código", 140, True),
            ("pasillo", "Pasillo", 90, True),
            ("cantidad", "Cant", 70, True),
            ("unitario", "Unit", 110, True),
            ("total", "Total", 110, True),
            ("id", "ID", 0, False),
        ]

        for key, title, width, stretch in columns:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=width, stretch=stretch)
            if key == "id":
                self.tree.column(key, width=0, stretch=False)

        # ─────────────────────────────────────────────
        # Cargar datos iniciales (NO marca dirty)
        # ─────────────────────────────────────────────
        self._load_from_df(arts_df)
        self.refresh()

    # ─────────────────────────────────────────────
    # Carga inicial
    # ─────────────────────────────────────────────
    def _load_from_df(self, df):
        """
        Convierte DataFrame a estructura interna.
        """
        for _, r in df.iterrows():
            item = {
                "id": str(r["id"]),
                "nombre": r["nombre"],
                "codigo": r["codigo"],
                "pasillo": r["pasillo"],
                "cantidad": int(r["cantidad"]),
                "unitario": float(r["unitario"]),
            }
            item["total"] = item["cantidad"] * item["unitario"]
            self.items.append(item)

    # ─────────────────────────────────────────────
    # Render
    # ─────────────────────────────────────────────
    def refresh(self):
        """
        Redibuja la tabla completa.
        """
        self.tree.delete(*self.tree.get_children())

        for it in self.items:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    it["nombre"],
                    it["codigo"],
                    it["pasillo"],
                    it["cantidad"],
                    money(it["unitario"]),
                    money(it["total"]),
                    it["id"],
                ),
            )

    # ─────────────────────────────────────────────
    # API pública (usada por Events)
    # ─────────────────────────────────────────────
    def was_modified(self) -> bool:
        """
        Indica si los artículos fueron modificados por el usuario.
        """
        return self._dirty

    def selected_item_id(self):
        """
        Devuelve el id del artículo seleccionado.
        """
        sel = self.tree.selection()
        if not sel:
            return None

        values = self.tree.item(sel[0], "values")
        return values[6]

    def remove_item(self, item_id):
        """
        Elimina un artículo por id.
        """
        self.items = [it for it in self.items if it["id"] != item_id]
        self._dirty = True          # 👈 cambio real
        self.refresh()

    def get_items(self):
        """
        Devuelve artículos listos para guardar.
        """
        return [
            {
                "id": it["id"],
                "pasillo": it["pasillo"],
                "cantidad": it["cantidad"],
                "unitario": it["unitario"],
            }
            for it in self.items
        ]

    # ─────────────────────────────────────────────
    # Edición inline
    # ─────────────────────────────────────────────
    def _on_double_click(self, event):
        """
        Maneja edición inline por doble clic.
        """
        iid = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if not iid or not col:
            return

        col_index = int(col[1:]) - 1

        # Columnas editables:
        # 2 = pasillo, 3 = cantidad, 4 = unitario
        if col_index not in (2, 3, 4):
            return

        values = self.tree.item(iid, "values")
        item_id = values[6]

        item = next((x for x in self.items if x["id"] == item_id), None)
        if not item:
            return

        self._open_editor_popup(item, col_index)

    def _open_editor_popup(self, item, col_index):
        """
        Abre popup de edición.
        """
        popup = tk.Toplevel(self)
        popup.transient(self)
        popup.grab_set()
        popup.resizable(False, False)
        popup.geometry("260x150")

        frame = ttk.Frame(popup, padding=12)
        frame.pack(fill="both", expand=True)

        # ─────────────────────────────────────────────
        # Editar pasillo
        # ─────────────────────────────────────────────
        if col_index == 2:
            ttk.Label(frame, text="Pasillo").pack(anchor="w")
            cb = ttk.Combobox(frame, values=PASILLOS, state="readonly")
            cb.set(item["pasillo"])
            cb.pack(fill="x", pady=6)

            def apply():
                item["pasillo"] = cb.get()
                self._dirty = True        # 👈 cambio real
                self.refresh()
                popup.destroy()

        # ─────────────────────────────────────────────
        # Editar cantidad / unitario
        # ─────────────────────────────────────────────
        else:
            field = "cantidad" if col_index == 3 else "unitario"
            label = "Cantidad" if field == "cantidad" else "Precio unitario"

            ttk.Label(frame, text=label).pack(anchor="w")
            entry = ttk.Entry(frame)
            entry.insert(0, item[field])
            entry.pack(fill="x", pady=6)

            def apply():
                try:
                    value = (
                        fint(entry.get())
                        if field == "cantidad"
                        else ffloat(entry.get())
                    )
                except Exception:
                    messagebox.showwarning("Error", "Valor inválido")
                    return

                item[field] = value
                item["total"] = item["cantidad"] * item["unitario"]
                self._dirty = True        # 👈 cambio real
                self.refresh()
                popup.destroy()

        ttk.Button(frame, text="Aplicar", command=apply).pack(pady=10)
