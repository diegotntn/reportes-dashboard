from tkinter import ttk
from datetime import datetime, date
from tkcalendar import DateEntry
from utils.constants import MOTIVOS, ZONAS


class EditDevolucionForm(ttk.LabelFrame):
    """
    Formulario de datos generales de la devolución.
    """

    def __init__(self, parent, devol_row):
        super().__init__(parent, text="Datos de la devolución", padding=10)

        # ===== Fecha =====
        self.fecha = DateEntry(self, date_pattern="yyyy-mm-dd")
        try:
            self.fecha.set_date(
                datetime.strptime(str(devol_row.get("fecha", "")), "%Y-%m-%d").date()
            )
        except Exception:
            self.fecha.set_date(date.today())

        # ===== Campos =====
        self.folio = ttk.Entry(self, width=18)
        self.folio.insert(0, devol_row.get("folio", ""))

        self.cliente = ttk.Entry(self, width=28)
        self.cliente.insert(0, devol_row.get("cliente", ""))

        self.direccion = ttk.Entry(self, width=32)
        self.direccion.insert(0, devol_row.get("direccion", ""))

        self.zona = ttk.Combobox(self, values=ZONAS, state="readonly", width=10)
        self.zona.set(devol_row.get("zona", ""))

        self.motivo = ttk.Combobox(self, values=MOTIVOS, state="readonly", width=26)
        self.motivo_otro = ttk.Entry(self, width=28)

        mot = str(devol_row.get("motivo", "")).lower()
        if mot in MOTIVOS:
            self.motivo.set(mot)
        else:
            self.motivo.current(0)
            self.motivo_otro.insert(0, mot)

        # ===== Layout =====
        campos = [
            ("Fecha", self.fecha, 0, 0),
            ("Folio", self.folio, 0, 1),
            ("Cliente", self.cliente, 0, 2),
            ("Dirección", self.direccion, 0, 3),
            ("Zona", self.zona, 2, 0),
            ("Motivo", self.motivo, 2, 1),
            ("Otro motivo", self.motivo_otro, 2, 2),
        ]

        for txt, w, r, c in campos:
            ttk.Label(self, text=txt).grid(row=r, column=c, sticky="w", padx=8)
            w.grid(row=r + 1, column=c, sticky="w", padx=8, pady=(0, 10))

    # ==========================================================
    # MÉTODO QUE FALTABA (CLAVE PARA EL ERROR)
    # ==========================================================
    def get_data(self) -> dict:
        """
        Devuelve los datos del formulario listos para guardar.
        """
        motivo = self.motivo.get().strip()
        motivo_otro = self.motivo_otro.get().strip()

        return {
            "fecha": self.fecha.get_date().strftime("%Y-%m-%d"),
            "folio": self.folio.get().strip(),
            "cliente": self.cliente.get().strip(),
            "direccion": self.direccion.get().strip(),
            "zona": self.zona.get().strip(),
            "motivo": motivo_otro if motivo_otro else motivo,
        }
