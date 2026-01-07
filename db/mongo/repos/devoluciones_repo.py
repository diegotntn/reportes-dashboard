from datetime import datetime
import pandas as pd


class DevolucionesRepo:
    def __init__(self, db):
        self.col = db.devoluciones

    # ───────────── Helpers ─────────────
    @staticmethod
    def _to_dt(value):
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value))

    @staticmethod
    def _df(docs):
        return pd.DataFrame(docs) if docs else pd.DataFrame()

    # ───────────── CRUD ─────────────
    def insertar(
        self,
        *,
        devolucion_id: str,
        fecha,
        folio: str,
        cliente: str,
        direccion: str,
        motivo: str,
        zona: str,
        total: float,
        articulos: list[dict],
        vendedor_id=None,
        estatus="pendiente",
    ):
        doc = {
            "_id": devolucion_id,
            "fecha": self._to_dt(fecha),
            "folio": folio,
            "cliente": cliente,
            "direccion": direccion,
            "motivo": motivo,
            "zona": zona,
            "total": float(total),
            "articulos": articulos or [],
            "vendedor_id": vendedor_id,
            "estatus": estatus,
            "created_at": datetime.utcnow(),
        }
        self.col.insert_one(doc)

    def actualizar(self, devolucion_id: str, *, data: dict):
        if not data:
            return
        self.col.update_one({"_id": devolucion_id}, {"$set": data})

    def eliminar(self, devolucion_id: str):
        self.col.delete_one({"_id": devolucion_id})

    def eliminar_todas(self):
        self.col.delete_many({})

    # ───────────── Queries simples ─────────────
    def listar(self, filtros: dict) -> pd.DataFrame:
        docs = list(
            self.col.find(filtros).sort([("fecha", -1), ("folio", -1)])
        )
        for d in docs:
            d["id"] = d.pop("_id")
            d["fecha"] = d["fecha"].date().isoformat()
        return self._df(docs)

    def articulos(self, devolucion_id: str) -> pd.DataFrame:
        d = self.col.find_one({"_id": devolucion_id})
        if not d:
            return pd.DataFrame()

        rows = []
        for i, a in enumerate(d.get("articulos", [])):
            r = dict(a)
            r["id"] = str(i)
            rows.append(r)

        return self._df(rows)
