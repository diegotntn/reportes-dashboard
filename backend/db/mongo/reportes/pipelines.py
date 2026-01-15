"""
Pipelines de MongoDB para reportes de devoluciones.

REGLAS CLAVE:
- NUNCA devolver nulls para métricas numéricas
- El dinero sale normalizado desde Mongo (double)
- El service NO calcula importes, solo agrega
- Soporta fecha como Date o String (normalización interna)
- El casteo de ObjectId SIEMPRE se hace en Python
"""

# ─────────────────────────────────────────────
# DETALLE ANALÍTICO (BASE DE REPORTES)
# ─────────────────────────────────────────────
def pipeline_devoluciones_detalle(filtros: dict) -> list:
    filtro_fecha = filtros.get("fecha", {})

    print("\n🧩 [pipeline_devoluciones_detalle]")
    print("➡ Filtro fecha recibido:", filtro_fecha)

    return [
        # 1️⃣ Normalizar fecha
        {
            "$addFields": {
                "__fecha": {
                    "$cond": [
                        {"$eq": [{"$type": "$fecha"}, "date"]},
                        "$fecha",
                        {"$dateFromString": {"dateString": "$fecha"}}
                    ]
                }
            }
        },

        # 2️⃣ Match por fecha
        {"$match": {"__fecha": filtro_fecha}},

        # 3️⃣ Total piezas
        {
            "$addFields": {
                "total_piezas": {
                    "$sum": {
                        "$map": {
                            "input": {"$ifNull": ["$items", []]},
                            "as": "i",
                            "in": {"$ifNull": ["$$i.cantidad", 0]}
                        }
                    }
                }
            }
        },

        # 4️⃣ Unwind
        {"$unwind": "$items"},

        # 5️⃣ Proyección
        {
            "$project": {
                "_id": 0,
                "fecha": "$__fecha",
                "zona": 1,
                "pasillo": {"$ifNull": ["$items.pasillo", "—"]},
                "piezas": {"$toInt": {"$ifNull": ["$items.cantidad", 0]}},
                "importe": {
                    "$cond": [
                        {"$gt": ["$total_piezas", 0]},
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {"$toDouble": {"$ifNull": ["$items.cantidad", 0]}},
                                        {"$toDouble": "$total_piezas"}
                                    ]
                                },
                                {"$toDouble": {"$ifNull": ["$total", 0]}}
                            ]
                        },
                        0.0
                    ]
                },
                "devoluciones": {"$literal": 1}
            }
        }
    ]


# ─────────────────────────────────────────────
# RESUMEN POR DEVOLUCIÓN
# ─────────────────────────────────────────────
def pipeline_devoluciones_resumen(filtros: dict) -> list:
    filtro_fecha = filtros.get("fecha", {})

    print("\n🧩 [pipeline_devoluciones_resumen]")
    print("➡ Filtro fecha recibido:", filtro_fecha)

    return [
        {
            "$addFields": {
                "__fecha": {
                    "$cond": [
                        {"$eq": [{"$type": "$fecha"}, "date"]},
                        "$fecha",
                        {"$dateFromString": {"dateString": "$fecha"}}
                    ]
                }
            }
        },

        {"$match": {"__fecha": filtro_fecha}},

        {
            "$addFields": {
                "pasillos": {
                    "$setUnion": [
                        {
                            "$map": {
                                "input": {"$ifNull": ["$items", []]},
                                "as": "i",
                                "in": {"$ifNull": ["$$i.pasillo", None]}
                            }
                        },
                        []
                    ]
                }
            }
        },

        {
            "$project": {
                "_id": 0,
                "fecha": "$__fecha",
                "folio": 1,
                "cliente": 1,
                "zona": 1,
                "motivo": 1,
                "estatus": 1,
                "pasillos": {
                    "$reduce": {
                        "input": "$pasillos",
                        "initialValue": "",
                        "in": {
                            "$cond": [
                                {"$eq": ["$$value", ""]},
                                "$$this",
                                {"$concat": ["$$value", ", ", "$$this"]}
                            ]
                        }
                    }
                },
                "total": {"$toDouble": {"$ifNull": ["$total", 0]}}
            }
        },

        {"$sort": {"fecha": -1}}
    ]


# ─────────────────────────────────────────────
# ARTÍCULOS DE UNA DEVOLUCIÓN
# ─────────────────────────────────────────────
def pipeline_devolucion_articulos(devolucion_id: str) -> list:
    print("\n🧩 [pipeline_devolucion_articulos]")
    print("➡ devolucion_id:", devolucion_id)

    return [
        {
            "$match": {
                "$or": [
                    {"id": devolucion_id},
                    {"_id": devolucion_id}
                ]
            }
        },
        {"$unwind": "$items"},
        {
            "$project": {
                "_id": 0,
                "nombre": {"$ifNull": ["$items.descripcion", ""]},
                "codigo": {"$ifNull": ["$items.clave", ""]},
                "pasillo": {"$ifNull": ["$items.pasillo", "—"]},
                "cantidad": {"$toInt": {"$ifNull": ["$items.cantidad", 0]}},
                "unitario": {"$toDouble": {"$ifNull": ["$items.precio", 0]}}
            }
        }
    ]
