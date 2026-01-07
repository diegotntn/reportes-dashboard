from datetime import datetime


def rango_fechas(desde=None, hasta=None) -> dict:
    """
    Genera filtro Mongo para rango de fechas.
    """
    if not (desde and hasta):
        return {}

    d1 = _to_dt(desde)
    d2 = _to_dt(hasta).replace(hour=23, minute=59, second=59)

    return {"fecha": {"$gte": d1, "$lte": d2}}


def por_vendedor(vendedor_id=None) -> dict:
    return {"vendedor_id": vendedor_id} if vendedor_id else {}


def por_estatus(estatus=None) -> dict:
    return {"estatus": estatus} if estatus else {}


def combinar_filtros(*filtros: dict) -> dict:
    """
    Combina múltiples filtros Mongo ignorando vacíos.
    """
    query = {}
    for f in filtros:
        query.update(f)
    return query


# helper local
def _to_dt(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))
