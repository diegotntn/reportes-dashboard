"""
Mapper de Artículo.

RESPONSABILIDAD:
- Convertir estructuras UI / dict → Articulo (dominio)
- Convertir Articulo (dominio) → dict para persistencia

NO HACE:
- Validaciones de negocio
- Acceso a DB
"""

from backend.domain.devoluciones import Articulo


# ───────────────────────── UI → DOMINIO ─────────────────────────
def articulo_from_ui(data: dict) -> Articulo:
    """
    Convierte un dict proveniente de la UI en Articulo de dominio.
    """

    return Articulo.from_dict({
        "codigo": data.get("clave"),
        "nombre": data.get("descripcion"),
        "cantidad": data.get("cantidad"),
        "unitario": data.get("precio"),
        "pasillo": data.get("pasillo"),
    })


# ───────────────────────── DOMINIO → DB ─────────────────────────
def articulo_to_persistence(articulo: Articulo) -> dict:
    """
    Convierte un Articulo de dominio a dict para Mongo.
    """

    return {
        "codigo": articulo.codigo,
        "nombre": articulo.nombre,
        "pasillo": articulo.pasillo,
        "cantidad": articulo.cantidad,
        "precio": articulo.unitario,
        "subtotal": articulo.total,
    }
