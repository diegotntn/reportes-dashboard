import pandas as pd
from backend.domain.personal import Persona


class PersonalService:
    """
    Lógica de negocio para PERSONAL OPERATIVO y ASIGNACIONES.

    REGLAS:
    - Services NO acceden a Mongo directamente
    - Services usan SOLO sus repositorios
    - Services normalizan datos para la UI
    - NO usan ReportesQueries
    """

    def __init__(self, personal_repo):
        """
        personal_repo: PersonalRepo
        """
        self.repo = personal_repo

    # ─────────────────────────
    # PERSONAL
    # ─────────────────────────
    def crear_persona(self, nombre: str) -> str:
        persona = Persona(
            id="tmp",
            nombre=(nombre or "").strip()
        )
        persona.validar_nombre()
        return self.repo.crear(persona.nombre)

    def listar_personal(self, *, solo_activos: bool = True) -> pd.DataFrame:
        """
        Devuelve personal (activo o completo).
        """
        return self.repo.listar(solo_activos=solo_activos)

    def listar_personal_operativo(self) -> pd.DataFrame:
        """
        Devuelve personal activo operativo.
        (No filtra vendedores aquí; eso pertenece a otro dominio)
        """
        return self.repo.listar(solo_activos=True)

    # ─────────────────────────
    # ASIGNACIONES (ADMIN / UI)
    # ─────────────────────────
    def crear_asignacion(self, pasillo, persona_nombre, desde, hasta) -> str:
        persona_id = self._resolver_persona_id(persona_nombre)
        self._validar_fechas(desde, hasta)

        return self.repo.crear_asignacion(
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
    ) -> None:
        if not asignacion_id:
            raise ValueError("Asignación no especificada")

        persona_id = self._resolver_persona_id(persona_nombre)
        self._validar_fechas(desde, hasta)

        self.repo.actualizar_asignacion(
            asignacion_id=asignacion_id,
            pasillo=pasillo,
            persona_id=persona_id,
            fecha_desde=desde,
            fecha_hasta=hasta
        )

    def listar_asignaciones(self) -> list[dict]:
        """
        Devuelve asignaciones normalizadas para la UI.
        """
        asignaciones = self.repo.listar_asignaciones()

        if asignaciones.empty:
            return []

        personal = self.repo.listar(solo_activos=False)

        if personal.empty:
            return []

        mapa_personas = dict(
            zip(personal["id"].astype(str), personal["nombre"])
        )

        salida = []
        for _, r in asignaciones.iterrows():
            salida.append({
                "id": str(r.get("id")),
                "pasillo": r.get("pasillo", ""),
                "persona": mapa_personas.get(str(r.get("persona_id")), ""),
                "desde": r.get("fecha_desde", ""),
                "hasta": r.get("fecha_hasta") or "",
            })

        return salida

    # ─────────────────────────
    # REPORTES (USADO POR ReportesService)
    # ─────────────────────────
    def obtener_asignaciones_activas(self, *, desde, hasta) -> list[dict]:
        """
        Devuelve asignaciones ACTIVAS en un periodo.
        Usado EXCLUSIVAMENTE por ReportesService.
        """

        df = self.repo.listar_asignaciones_activas(
            desde=desde,
            hasta=hasta
        )

        if df.empty:
            return []

        salida = []
        for _, r in df.iterrows():
            salida.append({
                "pasillo": r.get("pasillo", ""),
                "persona_id": str(r.get("persona_id")),
            })

        return salida

    # ─────────────────────────
    # VALIDACIONES
    # ─────────────────────────
    def _resolver_persona_id(self, nombre: str) -> str:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("Nombre de persona requerido")

        df = self.repo.listar(solo_activos=False)

        if df.empty:
            raise ValueError("No hay personal registrado")

        match = df[df["nombre"] == nombre]
        if match.empty:
            raise ValueError("Persona no encontrada")

        return str(match.iloc[0]["id"])

    def _validar_fechas(self, desde, hasta) -> None:
        if desde and hasta and hasta < desde:
            raise ValueError(
                "La fecha hasta no puede ser menor que la fecha desde"
            )
