import tkinter as tk
from tkinter import ttk
import pandas as pd

from ui.reportes.renderers.tk_tables import TkTableRenderer
from utils.helpers import money


class DetalleView(ttk.Frame):
    """
    Vista Detalle.

    RESPONSABILIDADES:
    - Mostrar KPIs (importe / piezas)
    - Renderizar tabla de detalle (Treeview)
    - Mostrar folio real al inicio
    - Reservar columna Estado (vacía)
    - Mostrar columna Zona
    - Filtrar por Zona
    - Redondear valores numéricos

    ❌ NO lógica de negocio
    ❌ NO Mongo
    ❌ NO cálculos
    """

    TITLE = "Detalle"

    def __init__(self, parent):
        super().__init__(parent)

        # DataFrame base sin filtros
        self._df_original = pd.DataFrame()

        # ───────────────── KPI + FILTRO ─────────────────
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=(8, 4))

        # KPIs
        self.lbl_importe = ttk.Label(top, font=("Segoe UI", 11, "bold"))
        self.lbl_piezas = ttk.Label(top, font=("Segoe UI", 11, "bold"))

        # Filtro por Zona
        ttk.Label(top, text="Zona:").pack(side="right", padx=(0, 4))

        self.var_zona = tk.StringVar(value="Todas")

        self.cb_zona = ttk.Combobox(
            top,
            textvariable=self.var_zona,
            state="readonly",
            width=10
        )
        self.cb_zona.pack(side="right", padx=(0, 12))
        self.cb_zona.bind("<<ComboboxSelected>>", self._aplicar_filtro_zona)

        # ───────────────── TABLA ─────────────────
        self.table = TkTableRenderer(height=14)
        self.table_container = ttk.Frame(self)
        self.table_container.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    # ───────────────────────── API ─────────────────────────
    def render(self, data: dict) -> None:
        """
        data esperado:
        {
            "kpis": {"importe": bool, "piezas": bool},
            "resumen": {"importe_total": float, "piezas_total": int},
            "tabla": DataFrame | list[dict]
        }
        """

        kpis = data.get("kpis", {})
        resumen = data.get("resumen", {})
        tabla = data.get("tabla")

        # ───────────────── NORMALIZAR TABLA ─────────────────
        if tabla is None:
            df = pd.DataFrame()
        elif isinstance(tabla, list):
            df = pd.DataFrame(tabla)
        elif isinstance(tabla, pd.DataFrame):
            df = tabla.copy()
        else:
            raise TypeError(
                "DetalleView.render → 'tabla' debe ser DataFrame o list[dict]"
            )

        df = self._asegurar_columnas(df)
        df = self._redondear_numeros(df)

        # Guardar DF base (para filtros)
        self._df_original = df.copy()

        # ───────────────── LIMPIAR KPIs ─────────────────
        for w in self.lbl_importe.master.winfo_children():
            if isinstance(w, ttk.Label):
                w.pack_forget()

        # ───────────────── MOSTRAR KPIs ─────────────────
        if kpis.get("importe"):
            self.lbl_importe.config(
                text=f"Importe total: {money(resumen.get('importe_total', 0))}"
            )
            self.lbl_importe.pack(side="left", padx=(0, 20))

        if kpis.get("piezas"):
            self.lbl_piezas.config(
                text=f"Piezas totales: {resumen.get('piezas_total', 0)}"
            )
            self.lbl_piezas.pack(side="left")

        # ───────────────── TABLA VACÍA ─────────────────
        if df.empty:
            self.cb_zona["values"] = ["Todas"]
            self.var_zona.set("Todas")
            self._render_tabla(df)
            return

        # ───────────────── CONFIGURAR FILTRO ZONA ─────────────────
        zonas = sorted(
            z for z in df["zona"].dropna().astype(str).unique() if z
        )

        self.cb_zona["values"] = ["Todas"] + zonas
        self.var_zona.set("Todas")

        # ───────────────── RENDER FINAL ─────────────────
        self._render_tabla(df)

    # ───────────────────────── FILTRO ─────────────────────────
    def _aplicar_filtro_zona(self, _event=None) -> None:
        if self._df_original.empty or "zona" not in self._df_original.columns:
            return

        zona = self.var_zona.get()

        if zona == "Todas":
            df = self._df_original.copy()
        else:
            df = self._df_original[self._df_original["zona"] == zona].copy()

        df = self._asegurar_columnas(df)
        df = self._redondear_numeros(df)

        self._render_tabla(df)

    # ───────────────────────── HELPERS ─────────────────────────
    def _render_tabla(self, df: pd.DataFrame) -> None:
        """
        Renderiza el DataFrame en la tabla Treeview.
        """
        for w in self.table_container.winfo_children():
            w.destroy()

        columns = list(df.columns)
        rows = df.values.tolist()

        self.table.render(
            parent=self.table_container,
            columns=columns,
            data=rows,
            headings=columns
        )

    def _asegurar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Garantiza columnas base en orden correcto.
        """
        df = df.copy()

        if "folio" not in df.columns:
            df.insert(0, "folio", "")

        if "estado" not in df.columns:
            df.insert(1, "estado", "")

        if "zona" not in df.columns:
            df.insert(2, "zona", "")

        return df

    def _redondear_numeros(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Redondea columnas numéricas para presentación.
        """
        df = df.copy()

        columnas_money = {
            "unitario",
            "total",
            "importe",
            "precio",
            "subtotal"
        }

        columnas_enteras = {
            "cantidad",
            "piezas"
        }

        for col in df.columns:
            col_lower = col.lower()

            if col_lower in columnas_money:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

            elif col_lower in columnas_enteras:
                df[col] = (
                    pd.to_numeric(df[col], errors="coerce")
                    .fillna(0)
                    .astype(int)
                )

        return df
