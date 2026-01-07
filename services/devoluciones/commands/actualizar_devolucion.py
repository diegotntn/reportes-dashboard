"""
Command: actualizar_devolucion
Actualiza encabezado y/o artículos de una devolución.

REGLAS (modo estricto):
- No se normalizan datos inválidos
- No se permiten artículos incompletos
- Se falla temprano con mensajes claros
"""

from domain.devoluciones import Devolucion, Articulo
from datetime import datetime, date


def _to_datetime(value):
    """Convierte date | datetime | str a datetime (inicio del día)."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        raise ValueError(f"Fecha inválida: {value}")


def actualizar_devolucion(
    *,
    db,
    devolucion_id,
    fecha=None,
    folio=None,
    cliente=None,
    direccion=None,
    motivo=None,
    zona=None,
    items=None,
    vendedor_id=None,
    estatus=None,
):
    """
    Actualiza una devolución existente.
    Puede actualizar encabezado y/o artículos.
    """

    # ───────────────────────── Validaciones básicas ─────────────────────────
    if not devolucion_id:
        raise ValueError("Devolución no especificada.")

    if items is not None and not isinstance(items, list):
        raise TypeError("items debe ser una lista de artículos.")

    # ───────────────────────── 1️⃣ Validación de dominio ─────────────────────────
    if items is not None:
        devolucion = Devolucion(
            id=devolucion_id,
            folio=folio or "",
            cliente=cliente or "",
            direccion=direccion or "",
            motivo=motivo or "",
            zona=zona or "",
            vendedor_id=vendedor_id,
            estatus=estatus or "pendiente",
        )

        for idx, it in enumerate(items, start=1):

            if not isinstance(it, dict):
                raise TypeError(f"Artículo #{idx} no es un diccionario.")

            # Campos obligatorios
            faltantes = [
                k for k in ("clave", "descripcion", "cantidad", "precio")
                if it.get(k) is None
            ]
            if faltantes:
                raise ValueError(
                    f"Artículo #{idx} incompleto. Faltan: {', '.join(faltantes)}"
                )

            try:
                cantidad = int(it["cantidad"])
                precio = float(it["precio"])
            except Exception:
                raise ValueError(
                    f"Artículo #{idx} tiene cantidad o precio inválidos."
                )

            if cantidad <= 0:
                raise ValueError(f"Artículo #{idx} tiene cantidad <= 0.")

            if precio < 0:
                raise ValueError(f"Artículo #{idx} tiene precio negativo.")

            devolucion.articulos.append(
                Articulo.from_dict({
                    "codigo": it["clave"],
                    "nombre": it["descripcion"],
                    "cantidad": cantidad,
                    "unitario": precio,
                    "pasillo": it.get("pasillo"),
                })
            )

        # Validación de reglas del dominio
        devolucion.validar()

    # ───────────────────────── 2️⃣ Persistencia ─────────────────────────
    return db.actualizar_devolucion(
        devolucion_id=devolucion_id,
        fecha=_to_datetime(fecha) if fecha is not None else None,
        folio=folio,
        cliente=cliente,
        direccion=direccion,
        motivo=motivo,
        zona=zona,
        items=items,
        vendedor_id=vendedor_id,
        estatus=estatus,
    )
