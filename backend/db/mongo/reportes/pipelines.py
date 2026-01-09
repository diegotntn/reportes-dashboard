"""
Pipelines de MongoDB para reportes de devoluciones.

REGLAS CLAVE:
- NUNCA devolver nulls para métricas numéricas
- El dinero sale normalizado desde Mongo (double)
- El service NO calcula importes, solo agrega
- El casteo de ObjectId SIEMPRE se hace en Python
"""

from bson import ObjectId


# ─────────────────────────────────────────────
def pipeline_devoluciones_detalle(filtros: dict) -> list:
    """
    Pipeline de detalle por artículo (para reportes).

    Salida por documento:
    - fecha
    - zona
    - pasillo
    - piezas
    - importe (prorrateado desde el total del documento)
    - devoluciones (=1)
    """

    return [
        # ───── Filtro base ─────
        {"$match": filtros},

        # ───── Total de piezas por documento ─────
        {
            "$addFields": {
                "total_piezas": {
                    "$sum": {
                        "$ifNull": ["$articulos.cantidad", []]
                    }
                }
            }
        },

        # ───── Expandir artículos ─────
        {"$unwind": "$articulos"},

        # ───── Proyección normalizada ─────
        {
            "$project": {
                "_id": 0,

                # Dimensiones
                "fecha": 1,
                "zona": 1,
                "pasillo": {
                    "$ifNull": ["$articulos.pasillo", "—"]
                },

                # Métricas
                "piezas": {
                    "$toInt": {
                        "$ifNull": ["$articulos.cantidad", 0]
                    }
                },

                # ───── IMPORTE PRORRATEADO REAL ─────
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
                                {
                                    "$toDouble": {
                                        "$ifNull": ["$total", 0]
                                    }
                                }
                            ]
                        },
                        0.0
                    ]
                },

                # Indicador
                "devoluciones": {"$literal": 1},
            }
        },
    ]


# ─────────────────────────────────────────────
def pipeline_devoluciones_resumen(filtros: dict) -> list:
    return [
        {"$match": filtros},

        # Extraer pasillos únicos desde artículos
        {
            "$addFields": {
                "pasillos": {
                    "$setUnion": [
                        {
                            "$map": {
                                "input": "$articulos",
                                "as": "a",
                                "in": {
                                    "$ifNull": ["$$a.pasillo", None]
                                }
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
                "id": 1,                # UUID de negocio
                "fecha": 1,
                "folio": 1,
                "cliente": 1,
                "zona": 1,
                "motivo": 1,
                "estatus": 1,

                # Convertir pasillos a texto
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

                "total": {
                    "$toDouble": {
                        "$ifNull": ["$total", 0]
                    }
                },
            }
        },

        {"$sort": {"fecha": -1, "folio": -1}},
    ]


# ─────────────────────────────────────────────
def pipeline_devolucion_articulos(devolucion_id: str) -> list:
    return [
        {
            "$match": {
                "$or": [
                    {"id": devolucion_id},
                    {"_id": devolucion_id}  # por si algún registro viejo
                ]
            }
        },
        {"$unwind": "$articulos"},
        {
            "$project": {
                "_id": 0,
                "nombre": {
                    "$ifNull": ["$articulos.nombre", ""]
                },
                "codigo": {
                    "$ifNull": ["$articulos.codigo", ""]
                },
                "pasillo": {
                    "$ifNull": ["$articulos.pasillo", "—"]
                },
                "cantidad": {
                    "$toInt": {
                        "$ifNull": ["$articulos.cantidad", 0]
                    }
                },
                "unitario": {
                    "$toDouble": {
                        "$ifNull": ["$articulos.precio", 0]
                    }
                },
            }
        },
    ]
