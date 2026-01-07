from ui.common.dialogs import BaseDialog
from .form import EditDevolucionForm
from .table import EditArticulosTable
from .events import EditDevolucionEvents

from tkinter import ttk
import pandas as pd


class EditDevolucionDialog(BaseDialog):
    """
    Diálogo principal para editar una devolución.

    RESPONSABILIDAD:
    - Crear y acomodar subcomponentes (Form + Table + Footer)
    - Exponer referencias claras a Events
    - NO contiene lógica de negocio
    - Recibe datos ya resueltos (DataFrames, filas, ids)
    """

    def __init__(
        self,
        parent,
        service,
        devolucion_id: str,
        devol_row,
        arts_df: pd.DataFrame,
        on_saved=None,
    ):
        # ─────────────────────────────────────────────
        # Validación de contrato (CRÍTICA)
        # ─────────────────────────────────────────────
        if arts_df is None:
            raise RuntimeError(
                "EditDevolucionDialog recibió arts_df=None. "
                "El caller DEBE asignar el retorno de obtener_articulos()."
            )

        if not isinstance(arts_df, pd.DataFrame):
            raise TypeError(
                f"arts_df debe ser pandas.DataFrame, "
                f"se recibió: {type(arts_df)}"
            )

        super().__init__(
            parent=parent,
            title="Editar devolución",
            modal=True,
            resizable=True,
            geometry="980x620",
        )

        # ─────────────────────────────────────────────
        # Events (orquestador de acciones)
        # ─────────────────────────────────────────────
        self.events = EditDevolucionEvents(
            service=service,
            devolucion_id=devolucion_id,
            on_saved=on_saved,
            dialog=self,
        )

        # ─────────────────────────────────────────────
        # Layout del contenedor base
        # ─────────────────────────────────────────────
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        # ─────────────────────────────────────────────
        # Formulario (encabezado)
        # ─────────────────────────────────────────────
        self.form = EditDevolucionForm(
            parent=self.container,
            devol_row=devol_row,
        )
        self.form.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(12, 8),
        )

        # ─────────────────────────────────────────────
        # Tabla de artículos
        # ─────────────────────────────────────────────
        self.table = EditArticulosTable(
            parent=self.container,
            arts_df=arts_df,
        )
        self.table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 8),
        )

        # ─────────────────────────────────────────────
        # Footer (acciones)
        # ─────────────────────────────────────────────
        self.footer = ttk.Frame(self.container)
        self.footer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 12),
        )

        self.footer.columnconfigure(0, weight=1)

        # Botón eliminar artículo
        self.btn_eliminar = ttk.Button(
            self.footer,
            text="Eliminar artículo",
        )
        self.btn_eliminar.grid(row=0, column=1, padx=6)

        # Botón guardar
        self.btn_guardar = ttk.Button(
            self.footer,
            text="Guardar cambios",
        )
        self.btn_guardar.grid(row=0, column=2, padx=6)

        # Botón cancelar
        self.btn_cancelar = ttk.Button(
            self.footer,
            text="Cancelar",
            command=self.destroy,
        )
        self.btn_cancelar.grid(row=0, column=3, padx=6)

        # ─────────────────────────────────────────────
        # Binding de eventos
        # ─────────────────────────────────────────────
        self.events.bind(
            form=self.form,
            table=self.table,
        )
