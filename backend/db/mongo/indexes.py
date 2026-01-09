from pymongo.database import Database
from .collections import (
    DEVOLUCIONES,
    PERSONAL,
    VENDEDORES,
    ASIGNACIONES,
    PRODUCTOS,
)


def ensure_indexes(db: Database):
    """
    Crea y asegura los índices necesarios para el sistema.
    Debe ejecutarse UNA SOLA VEZ al iniciar la app.
    """

    # ───────── DEVOLUCIONES ─────────
    col = db[DEVOLUCIONES]
    col.create_index("fecha")
    col.create_index("folio", unique=True)
    col.create_index("zona")
    col.create_index("vendedor_id")
    col.create_index("estatus")
    col.create_index("articulos.pasillo")

    # ───────── PERSONAL ─────────
    db[PERSONAL].create_index("activo")

    # ───────── VENDEDORES ─────────
    col = db[VENDEDORES]
    col.create_index("persona_id", unique=True)
    col.create_index("codigo", unique=True)
    col.create_index("zona")
    col.create_index("activo")

    # ───────── ASIGNACIONES ─────────
    col = db[ASIGNACIONES]
    col.create_index("pasillo")
    col.create_index("persona_id")
    col.create_index("fecha_desde")

    # ───────── PRODUCTOS ─────────
    col = db[PRODUCTOS]
    col.create_index("clave", unique=True)
    col.create_index("nombre")
    col.create_index("linea")
