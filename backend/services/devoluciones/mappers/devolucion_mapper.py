"""
Mapper de Devolución.

RESPONSABILIDAD:
- Construir Devolucion de dominio desde datos simples
- Convertir Devolucion a estructura persistible

NO HACE:
- Acceso a DB
- Reglas de negocio
"""

from backend.domain.devoluciones import Devolucion
from backend.services.devoluciones.mappers.articulo_mapper import (
    articulo_from_ui,
    articulo_to_persistence,
)


# ───────────────────────── UI → DOMINIO ─────────────────────────
def devolucion_from_ui(
    *,
    devolucion_id: str,
    folio,
    cliente,
    direccion,
    motivo,
    zona,
    vendedor_id=None,
    articulos=None,
    estatus=None,
) -> Devolucion:
    """
    Construye una Devolucion de dominio desde datos de UI.
    """

    devol = Devolucion(
        id=devolucion_id,
        folio=str(folio).strip(),
        cliente=str(cliente).strip(),
        direccion=str(direccion).strip(),
        motivo=str(motivo).strip(),
        zona=str(zona).strip(),
        vendedor_id=vendedor_id,
        estatus=estatus,
    )

    # Mapear artículos UI → dominio
    for it in articulos or []:
        devol.articulos.append(articulo_from_ui(it))

    return devol


# ───────────────────────── DOMINIO → DB ─────────────────────────
def devolucion_to_persistence(devol: Devolucion) -> dict:
    """
    Convierte una Devolucion de dominio a dict para persistencia.
    """

    return {
        "folio": devol.folio,
        "cliente": devol.cliente,
        "direccion": devol.direccion,
        "motivo": devol.motivo,
        "zona": devol.zona,
        "total": devol.total(),
        "articulos": [
            articulo_to_persistence(a)
            for a in devol.articulos
        ],
        "vendedor_id": devol.vendedor_id,
        "estatus": devol.estatus,
    }
