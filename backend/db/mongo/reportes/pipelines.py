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
    """
    Pipeline ANALÍTICO base.
    """

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
                        {
                            "$dateFromString": {
                                "dateString": "$fecha"
                            }
                        }
                    ]
                }
            }
        },

        # 2️⃣ Match por fecha
        {
            "$match": {
                "__fecha": filtro_fecha
            }
        },

        # 3️⃣ Total piezas
        {
            "$addFields": {
                "total_piezas": {
                    "$sum": {
                        "$map": {
                            "input": {"$ifNull": ["$articulos", []]},
                            "as": "a",
                            "in": {"$ifNull": ["$$a.cantidad", 0]}
                        }
                    }
                }
            }
        },

        # 4️⃣ Unwind
        {"$unwind": "$articulos"},

        # 5️⃣ Proyección
        {
            "$project": {
                "_id": 0,
                "fecha": "$__fecha",
                "zona": 1,
                "pasillo": {"$ifNull": ["$articulos.pasillo", "—"]},
                "piezas": {"$toInt": {"$ifNull": ["$articulos.cantidad", 0]}},
                "importe": {
                    "$cond": [
                        {"$gt": ["$total_piezas", 0]},
                        {
                            "$multiply": [
                                {
                                    "$divide": [
                                        {"$toDouble": {"$ifNull": ["$articulos.cantidad", 0]}},
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
                                "input": {"$ifNull": ["$articulos", []]},
                                "as": "a",
                                "in": {"$ifNull": ["$$a.pasillo", None]}
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
        {"$unwind": "$articulos"},
        {
            "$project": {
                "_id": 0,
                "nombre": {"$ifNull": ["$articulos.nombre", ""]},
                "codigo": {"$ifNull": ["$articulos.codigo", ""]},
                "pasillo": {"$ifNull": ["$articulos.pasillo", "—"]},
                "cantidad": {"$toInt": {"$ifNull": ["$articulos.cantidad", 0]}},
                "unitario": {"$toDouble": {"$ifNull": ["$articulos.precio", 0]}}
            }
        }
    ]
