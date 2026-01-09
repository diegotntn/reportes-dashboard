"""
Command: actualizar_devolucion

Actualiza encabezado y/o artículos de una devolución.

REGLAS (modo estricto):
- No se normalizan datos inválidos
- No se permiten artículos incompletos
- Se falla temprano con mensajes claros
"""

from datetime import datetime, date

from backend.domain.devoluciones import Devolucion, Articulo


# ───────────────────────── Helpers ─────────────────────────

def _to_datetime(value):
    """
    Convierte date | datetime | str a datetime (inicio del día).
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        raise ValueError(f"Fecha inválida: {value}")


# ───────────────────────── Command ─────────────────────────

def actualizar_devolucion(
    *,
    repo,
    devolucion_id: str,
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

    Parámetros
    ----------
    repo : DevolucionesRepo
        Repositorio de devoluciones
    devolucion_id : str
        ID de la devolución
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
                Articulo.from_dict(
                    {
                        "codigo": it["clave"],
                        "nombre": it["descripcion"],
                        "cantidad": cantidad,
                        "unitario": precio,
                        "pasillo": it.get("pasillo"),
                    }
                )
            )

        # Validación estricta de reglas del dominio
        devolucion.validar()

    # ───────────────────────── 2️⃣ Persistencia ─────────────────────────
    data = {}

    if fecha is not None:
        data["fecha"] = _to_datetime(fecha)

    if folio is not None:
        data["folio"] = folio

    if cliente is not None:
        data["cliente"] = cliente

    if direccion is not None:
        data["direccion"] = direccion

    if motivo is not None:
        data["motivo"] = motivo

    if zona is not None:
        data["zona"] = zona

    if items is not None:
        data["articulos"] = items

    if vendedor_id is not None:
        data["vendedor_id"] = vendedor_id

    if estatus is not None:
        data["estatus"] = estatus

    if not data:
        return False

    repo.actualizar(
        devolucion_id=devolucion_id,
        data=data,
    )

    return True
