import pandas as pd
import uuid
from typing import Iterable, List, Dict, Any
from datetime import datetime, time

class PersonalRepo:
    """
    Repositorio de PERSONAL y ASIGNACIONES.

    RESPONSABILIDAD:
    - CRUD de personas
    - Lectura de asignaciones (pasillos / zonas / etc.)
    - Acceso directo a Mongo (único lugar permitido)
    """

    def __init__(self, db):
        self.personal_col = db.personal
        self.asignaciones_col = db.asignaciones

    # ─────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────
    @staticmethod
    def _to_df(docs: Iterable[Dict[str, Any]]) -> pd.DataFrame:
        if not docs:
            return pd.DataFrame()
        return pd.DataFrame(docs)

    @staticmethod
    def _normalizar_id(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for d in docs:
            d["id"] = d.pop("_id")
        return docs

    # ─────────────────────────────────────────
    # PERSONAL
    # ─────────────────────────────────────────
    def crear(self, nombre: str) -> str:
        persona_id = str(uuid.uuid4())

        self.personal_col.insert_one({
            "_id": persona_id,
            "nombre": nombre.strip(),
            "activo": True,
        })

        return persona_id

    def listar(self, *, solo_activos: bool = True) -> pd.DataFrame:
        filtro = {"activo": True} if solo_activos else {}

        docs = list(
            self.personal_col
            .find(filtro)
            .sort("nombre", 1)
        )

        docs = self._normalizar_id(docs)
        return self._to_df(docs)

    def actualizar(self, persona_id: str, nuevo_nombre: str) -> None:
        self.personal_col.update_one(
            {"_id": persona_id},
            {"$set": {"nombre": nuevo_nombre.strip()}}
        )

    def eliminar(self, persona_id: str) -> None:
        self.personal_col.delete_one({"_id": persona_id})

    def desactivar(self, persona_id: str) -> None:
        """
        En este sistema la desactivación es eliminación real.
        """
        self.eliminar(persona_id)

    # ─────────────────────────────────────────
    # ASIGNACIONES
    # ─────────────────────────────────────────
    
    def listar_asignaciones_activas(self, *, desde, hasta):
        """
        desde, hasta: date o datetime
        Mongo requiere datetime
        """

        if hasattr(desde, "year"):
            desde = datetime.combine(desde, time.min)

        if hasattr(hasta, "year"):
            hasta = datetime.combine(hasta, time.max)

        docs = list(
            self.asignaciones_col.find({
                "activo": True,
                "fecha": {
                    "$gte": desde,
                    "$lte": hasta
                }
            })
        )

        docs = self._normalizar_id(docs)
        return self._to_df(docs)