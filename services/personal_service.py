import pandas as pd
from domain.personal import Persona


class PersonalService:
    """
    Lógica de negocio para PERSONAL OPERATIVO y ASIGNACIONES.

    REGLAS:
    - Services NO acceden a Mongo directamente
    - Services normalizan datos para la UI
    """

    def __init__(self, db):
        self.db = db

    # ─────────────────────────
    # PERSONAL
    # ─────────────────────────
    def crear_persona(self, nombre: str) -> str:
        persona = Persona(
            id="tmp",
            nombre=(nombre or "").strip()
        )
        persona.validar_nombre()
        return self.db.crear_persona(persona.nombre)

    def listar_personal_operativo(self) -> pd.DataFrame:
        personal = pd.DataFrame(
            self.db.listar_personal(solo_activos=True)
        )

        if personal.empty:
            return personal

        # Normalizar Persona._id → id
        if "_id" in personal.columns:
            personal["id"] = personal["_id"].astype(str)

        vendedores = pd.DataFrame(
            self.db.listar_vendedores(solo_activos=True)
        )

        if vendedores.empty:
            return personal

        # persona_id YA referencia a Persona
        if "persona_id" in vendedores.columns:
            vendedores_persona_ids = set(
                vendedores["persona_id"].astype(str)
            )
        else:
            vendedores_persona_ids = set()

        return personal[
            ~personal["id"].isin(vendedores_persona_ids)
        ]

    # ─────────────────────────
    # ASIGNACIONES
    # ─────────────────────────
    def crear_asignacion(self, pasillo, persona_nombre, desde, hasta):
        persona_id = self._resolver_persona_id(persona_nombre)
        self._validar_fechas(desde, hasta)

        # 🔑 COINCIDE EXACTAMENTE con el repo
        return self.db.crear_asignacion(
            pasillo=pasillo,
            persona_id=persona_id,
            fecha_desde=desde,
            fecha_hasta=hasta
        )

    def actualizar_asignacion(
        self,
        asignacion_id,
        pasillo,
        persona_nombre,
        desde,
        hasta
    ):
        if not asignacion_id:
            raise ValueError("Asignación no especificada")

        persona_id = self._resolver_persona_id(persona_nombre)
        self._validar_fechas(desde, hasta)

        self.db.actualizar_asignacion(
            asignacion_id=asignacion_id,
            pasillo=pasillo,
            persona_id=persona_id,
            fecha_desde=desde,
            fecha_hasta=hasta
        )

    def listar_asignaciones(self) -> list[dict]:
        """
        Devuelve asignaciones LISTAS PARA LA UI.
        """

        asignaciones = pd.DataFrame(
            self.db.listar_asignaciones()
        )

        if asignaciones.empty:
            return []

        # Normalizar Asignacion._id → id
        if "_id" in asignaciones.columns:
            asignaciones["id"] = asignaciones["_id"].astype(str)

        if "persona_id" in asignaciones.columns:
            asignaciones["persona_id"] = asignaciones["persona_id"].astype(str)

        personal = pd.DataFrame(
            self.db.listar_personal(solo_activos=False)
        )

        if personal.empty:
            return []

        if "_id" in personal.columns:
            personal["id"] = personal["_id"].astype(str)

        mapa_personas = dict(
            zip(personal["id"], personal["nombre"])
        )

        salida = []
        for _, r in asignaciones.iterrows():
            salida.append({
                "id": r["id"],
                "pasillo": r.get("pasillo", ""),
                "persona": mapa_personas.get(r["persona_id"], ""),
                "desde": r.get("fecha_desde", ""),
                "hasta": r.get("fecha_hasta") or "",
            })

        return salida

    # ─────────────────────────
    # REPORTES
    # ─────────────────────────
    def obtener_asignaciones_activas(self, desde, hasta) -> list[dict]:
        """
        Devuelve asignaciones ACTIVAS en un periodo.
        Usado por ReportesService.
        """

        asignaciones = pd.DataFrame(
            self.db.listar_asignaciones()
        )

        if asignaciones.empty:
            return []

        if "_id" in asignaciones.columns:
            asignaciones["id"] = asignaciones["_id"].astype(str)

        if "persona_id" in asignaciones.columns:
            asignaciones["persona_id"] = asignaciones["persona_id"].astype(str)

        asignaciones = asignaciones[
            (asignaciones["fecha_desde"] <= hasta) &
            (asignaciones["fecha_hasta"] >= desde)
        ]

        if asignaciones.empty:
            return []

        personal = pd.DataFrame(
            self.db.listar_personal(solo_activos=True)
        )

        if personal.empty:
            return []

        if "_id" in personal.columns:
            personal["id"] = personal["_id"].astype(str)

        mapa_personas = dict(
            zip(personal["id"], personal["nombre"])
        )

        salida = []
        for _, r in asignaciones.iterrows():
            nombre = mapa_personas.get(r["persona_id"])
            if not nombre:
                continue

            salida.append({
                "pasillo": r.get("pasillo", ""),
                "persona": nombre
            })

        return salida

    # ─────────────────────────
    # VALIDACIONES
    # ─────────────────────────
    def _resolver_persona_id(self, nombre: str) -> str:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("Nombre de persona requerido")

        df = pd.DataFrame(
            self.db.listar_personal(solo_activos=False)
        )

        if df.empty:
            raise ValueError("No hay personal registrado")

        if "_id" in df.columns:
            df["id"] = df["_id"].astype(str)

        match = df[df["nombre"] == nombre]
        if match.empty:
            raise ValueError("Persona no encontrada")

        return match.iloc[0]["id"]

    def _validar_fechas(self, desde, hasta):
        if desde and hasta and hasta < desde:
            raise ValueError(
                "La fecha hasta no puede ser menor que la fecha desde"
            )
