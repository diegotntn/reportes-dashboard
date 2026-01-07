from tkinter import messagebox
from datetime import date


class PersonalEvents:
    """
    Callbacks de personal y asignaciones.
    """

    def __init__(self, service):
        self.service = service
        self.persona_id_sel = None
        self.asignacion_id = None

    # ───────── BIND ─────────
    def bind(self, form, tables):
        self.form = form
        self.tables = tables

        # Botones persona
        self.form.btn_add.config(command=self._agregar_persona)
        self.form.btn_clear.config(command=self._limpiar_form_persona)

        # Botones asignación
        self.form.btn_save_asig.config(command=self._guardar_asignacion)
        self.form.btn_cancel_asig.config(command=self._cancelar_edicion)

        # Selecciones tablas
        self.tables.tbl_personal.bind(
            "<<TreeviewSelect>>", self._on_select_persona
        )
        self.tables.tbl_asig.bind(
            "<<TreeviewSelect>>", self._on_select_asignacion
        )

    # ───────── REFRESH GENERAL ─────────
    def refresh_all(self):
        self._refresh_personal()
        self._refresh_asignaciones()

    # ───────── PERSONAS ─────────
    def _refresh_personal(self):
        self.tables.tbl_personal.delete(
            *self.tables.tbl_personal.get_children()
        )

        df = self.service.listar_personal_operativo()
        nombres = []

        for _, p in df.iterrows():
            self.tables.tbl_personal.insert(
                "", "end", values=(p["id"], p["nombre"])
            )
            nombres.append(p["nombre"])

        self.form.cb_persona["values"] = nombres

    def _agregar_persona(self):
        nombre = self.form.var_nombre.get().strip()
        if not nombre:
            return

        try:
            self.service.crear_persona(nombre)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.form.var_nombre.set("")
        self._refresh_personal()

    def _limpiar_form_persona(self):
        self.persona_id_sel = None
        self.form.var_nombre.set("")

    def _on_select_persona(self, _):
        sel = self.tables.tbl_personal.selection()
        if not sel:
            return

        pid, nombre = self.tables.tbl_personal.item(sel[0], "values")
        self.persona_id_sel = pid
        self.form.var_nombre.set(nombre)

    # ───────── ASIGNACIONES ─────────
    def _refresh_asignaciones(self):
        self.tables.tbl_asig.delete(
            *self.tables.tbl_asig.get_children()
        )

        for r in self.service.listar_asignaciones():
            self.tables.tbl_asig.insert(
                "",
                "end",
                iid=r["id"],  # id oculto, correcto
                values=(
                    r["pasillo"],   # ← PASILLO
                    r["persona"],   # ← PERSONA
                    r["desde"],     # ← DESDE
                    r["hasta"],     # ← HASTA
                )
            )


    def _guardar_asignacion(self):

        pasillo = self.form.var_pasillo.get()
        persona = self.form.var_persona.get()

        if not pasillo or not persona:
            messagebox.showwarning(
                "Datos incompletos",
                "Selecciona pasillo y persona"
            )
            return

        desde = self.form.dt_desde.get_date().isoformat()
        hasta = self.form.dt_hasta.get_date().isoformat()
        
        print("GUARDANDO ASIGNACIÓN:")
        print("Pasillo:", pasillo)
        print("Persona:", persona)
        print("Desde:", desde)
        print("Hasta:", hasta)

        try:
            if self.asignacion_id:
                self.service.actualizar_asignacion(
                    self.asignacion_id,
                    pasillo,
                    persona,
                    desde,
                    hasta
                )
            else:
                # ✅ AQUÍ SE INSERTA LA ASIGNACIÓN
                self.service.crear_asignacion(
                    pasillo,
                    persona,
                    desde,
                    hasta
                )
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self._cancelar_edicion()
        self.refresh_all()

    def _on_select_asignacion(self, _):
        sel = self.tables.tbl_asig.selection()
        if not sel:
            return

        r = self.tables.tbl_asig.item(sel[0], "values")
        self.asignacion_id = r[0]

        self.form.var_pasillo.set(r[1])
        self.form.var_persona.set(r[2])
        self.form.dt_desde.set_date(r[3])
        self.form.dt_hasta.set_date(r[4] or date.today())

        self.form.btn_save_asig.config(
            text="Actualizar asignación"
        )
        self.form.btn_cancel_asig.state(["!disabled"])

    def _cancelar_edicion(self):
        self.asignacion_id = None

        self.form.var_pasillo.set("")
        self.form.var_persona.set("")
        self.form.dt_desde.set_date(date.today())
        self.form.dt_hasta.set_date(date.today())

        self.form.btn_save_asig.config(
            text="Guardar asignación"
        )
        self.form.btn_cancel_asig.state(["disabled"])
