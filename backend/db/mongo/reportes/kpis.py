import pandas as pd


def pipeline_kpis_generales(filtros: dict) -> list:
    return [
        {"$match": filtros},
        {
            "$group": {
                "_id": None,
                "total_importe": {"$sum": "$total"},
                "total_devoluciones": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0}},
    ]


class KPIsQueries:
    def __init__(self, db):
        self.col = db.devoluciones

    def kpis_generales(self, filtros: dict) -> pd.DataFrame:
        data = list(self.col.aggregate(
            pipeline_kpis_generales(filtros)
        ))
        return pd.DataFrame(data)
