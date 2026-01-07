import pandas as pd
import uuid


class PersonalRepo:
    def __init__(self, db):
        self.col = db.personal

    @staticmethod
    def _df(docs):
        return pd.DataFrame(docs) if docs else pd.DataFrame()

    def crear(self, nombre: str) -> str:
        pid = str(uuid.uuid4())
        self.col.insert_one({
            "_id": pid,
            "nombre": nombre.strip(),
            "activo": True
        })
        return pid

    def listar(self, solo_activos: bool = True) -> pd.DataFrame:
        q = {"activo": True} if solo_activos else {}
        docs = list(self.col.find(q).sort("nombre"))
        for d in docs:
            d["id"] = d.pop("_id")
        return self._df(docs)

    def actualizar(self, persona_id: str, nuevo_nombre: str):
        self.col.update_one(
            {"_id": persona_id},
            {"$set": {"nombre": nuevo_nombre.strip()}}
        )

    def eliminar(self, persona_id: str):
        self.col.delete_one({"_id": persona_id})

    def desactivar(self, persona_id: str):
        # En tu sistema es eliminación real
        self.eliminar(persona_id)
