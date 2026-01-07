import pandas as pd
import uuid
from datetime import datetime


class VendedoresRepo:
    def __init__(self, db):
        self.col = db.vendedores
        self.personal = db.personal

    @staticmethod
    def _df(rows):
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def crear(self, persona_id: str, codigo: str, zona: str) -> str:
        vid = str(uuid.uuid4())
        self.col.insert_one({
            "_id": vid,
            "persona_id": persona_id,
            "codigo": codigo.strip(),
            "zona": zona,
            "activo": True,
            "fecha_alta": datetime.utcnow()
        })
        return vid

    def listar(self, solo_activos: bool = True) -> pd.DataFrame:
        q = {"activo": True} if solo_activos else {}
        docs = list(self.col.find(q))

        rows = []
        for v in docs:
            p = self.personal.find_one({"_id": v["persona_id"]})
            rows.append({
                "id": v["_id"],
                "persona_id": v["persona_id"],
                "codigo": v.get("codigo"),
                "zona": v.get("zona"),
                "nombre": p.get("nombre") if p else None,
                "activo": bool(v.get("activo", True)),
            })

        return self._df(rows)

    def desactivar(self, vendedor_id: str):
        self.col.update_one(
            {"_id": vendedor_id},
            {"$set": {"activo": False}}
        )
