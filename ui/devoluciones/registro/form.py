import tkinter as tk
from tkinter import ttk, StringVar
from tkcalendar import DateEntry

from utils.constants import MOTIVOS


# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

ZONAS = [
    "Z11","Z12","Z13","Z14","Z15","Z17","Z18",
    "Z19","Z20","Z21","Z22","Z23","Z27","Z28"
]

PASILLOS = ["P1", "P2", "P3", "P4"]


# ─────────────────────────────────────────────
# FORMULARIO: DATOS GENERALES DE LA DEVOLUCIÓN
# ─────────────────────────────────────────────
class RegistroForm(ttk.LabelFrame):
    """
    Datos generales de la devolución.
    """

    def __init__(self, parent):
        super().__init__(parent, text="Datos de la devolución", padding=10)

        self.fecha = DateEntry(self, date_pattern="yyyy-mm-dd")
        self.folio = ttk.Entry(self)
        self.cliente = ttk.Entry(self)
        self.direccion = ttk.Entry(self)

        self.zona = ttk.Combobox(self, values=ZONAS, state="readonly")
        self.zona.current(0)

        self.motivo = ttk.Combobox(self, values=MOTIVOS, state="readonly")
        self.motivo.current(0)

        self.motivo_otro = ttk.Entry(self)

        self._layout()

    # ─────────────────────────
    def _layout(self):
        campos = [
            ("Fecha", self.fecha, 0, 0),
            ("Folio", self.folio, 0, 1),
            ("Cliente", self.cliente, 0, 2),
            ("Dirección", self.direccion, 0, 3),
            ("Zona", self.zona, 2, 0),
            ("Motivo", self.motivo, 2, 1),
            ("Otro motivo", self.motivo_otro, 2, 2),
        ]

        for texto, widget, fila, col in campos:
            ttk.Label(self, text=texto).grid(row=fila, column=col, sticky="w")
            widget.grid(row=fila + 1, column=col, padx=8, pady=6, sticky="ew")

    # ─────────────────────────
    def get_data(self) -> dict:
        otro = self.motivo_otro.get().strip()
        return {
            "fecha": self.fecha.get_date(),
            "folio": self.folio.get().strip(),
            "cliente": self.cliente.get().strip(),
            "direccion": self.direccion.get().strip(),
            "zona": self.zona.get(),
            "motivo": otro.lower() if otro else self.motivo.get().lower(),
        }

    # ─────────────────────────
    def clear(self):
        for campo in (self.folio, self.cliente, self.direccion, self.motivo_otro):
            campo.delete(0, "end")

        self.motivo.current(0)
        self.zona.current(0)


# ─────────────────────────────────────────────
# FORMULARIO: ARTÍCULO (AUTOCOMPLETADO)
# ─────────────────────────────────────────────
class ArticuloForm(ttk.LabelFrame):
    """
    Formulario para agregar artículos.
    El usuario escribe código o nombre.
    """

    def __init__(self, parent):
        super().__init__(parent, text="Agregar artículo", padding=10)

        # ───── Variables ─────
        self.buscar_var = StringVar()
        self.codigo_var = StringVar()
        self.nombre_var = StringVar()
        self.precio_var = StringVar()
        self.pasillo_var = StringVar()
        self.cantidad_var = StringVar(value="1")

        # ───── Widgets ─────
        self.buscar = ttk.Entry(self, textvariable=self.buscar_var, width=45)

        self.codigo = ttk.Entry(self, textvariable=self.codigo_var, state="readonly")
        self.nombre = ttk.Entry(self, textvariable=self.nombre_var, state="readonly")
        self.precio = ttk.Entry(self, textvariable=self.precio_var, state="readonly")

        self.pasillo = ttk.Combobox(
            self,
            textvariable=self.pasillo_var,
            values=PASILLOS,
            width=6,
            state="disabled"
        )

        self.cantidad = ttk.Entry(self, textvariable=self.cantidad_var, width=6)

        # ───── Listbox autocomplete ─────
        self._listbox = tk.Listbox(self, height=6)
        self._listbox.place_forget()

        self._layout()

    # ─────────────────────────
    def _layout(self):
        fila = 0

        ttk.Label(self, text="Buscar (código o nombre)").grid(row=fila, column=0, sticky="w")
        self.buscar.grid(
            row=fila + 1, column=0, columnspan=3,
            padx=8, pady=6, sticky="ew"
        )

        fila += 2

        headers = ["Código", "Nombre", "Precio", "Pasillo", "Cant"]
        for i, h in enumerate(headers):
            ttk.Label(self, text=h).grid(row=fila, column=i, sticky="w")

        fila += 1

        self.codigo.grid(row=fila, column=0, padx=6, pady=4)
        self.nombre.grid(row=fila, column=1, padx=6, pady=4, sticky="ew")
        self.precio.grid(row=fila, column=2, padx=6, pady=4)
        self.pasillo.grid(row=fila, column=3, padx=6, pady=4)
        self.cantidad.grid(row=fila, column=4, padx=6, pady=4)

    # ─────────────────────────────────────────
    # AUTOCOMPLETADO (USADO POR EVENTS)
    # ─────────────────────────────────────────
    def mostrar_sugerencias(self, productos: list):
        if not productos:
            self.ocultar_sugerencias()
            return

        self._productos_cache = productos
        self._listbox.delete(0, tk.END)

        for p in productos:
            self._listbox.insert(
                tk.END,
                f"{p['clave']} — {p['nombre']}"
            )

        self.update_idletasks()
        x = self.buscar.winfo_x()
        y = self.buscar.winfo_y() + self.buscar.winfo_height()
        w = self.buscar.winfo_width()

        self._listbox.place(x=x, y=y, width=w)
        self._listbox.lift()

    def ocultar_sugerencias(self):
        self._listbox.place_forget()

    # ─────────────────────────
    # API PARA EVENTS
    # ─────────────────────────
    def set_producto(self, producto: dict, pasillo: str | None):
        self.codigo_var.set(producto.get("clave", ""))
        self.nombre_var.set(producto.get("nombre", ""))
        self.precio_var.set(f"{producto.get('lcd4', 0):.2f}")

        if pasillo:
            self.pasillo_var.set(pasillo)
            self.pasillo.config(state="disabled")
        else:
            self.pasillo_var.set("")
            self.pasillo.config(state="readonly")

    def get_data(self) -> dict:
        try:
            cantidad = int(self.cantidad_var.get())
        except ValueError:
            raise ValueError("Cantidad inválida")

        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")

        return {
            "clave": self.codigo_var.get(),
            "nombre": self.nombre_var.get(),
            "precio": float(self.precio_var.get() or 0),
            "pasillo": self.pasillo_var.get(),
            "cantidad": cantidad,
        }

    def clear(self):
        self.buscar_var.set("")
        self.codigo_var.set("")
        self.nombre_var.set("")
        self.precio_var.set("")
        self.pasillo_var.set("")
        self.cantidad_var.set("1")
        self.pasillo.config(state="disabled")
