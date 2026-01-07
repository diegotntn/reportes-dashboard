import uuid
from datetime import datetime, date

from domain.devoluciones import Devolucion
from services.devoluciones.mappers.devolucion_mapper import (
    devolucion_from_ui,
    devolucion_to_persistence,
)


def _normalizar_fecha(fecha):
    """
    MongoDB NO acepta datetime.date
    Convierte date → datetime (00:00:00)
    """
    if isinstance(fecha, date) and not isinstance(fecha, datetime):
        return datetime.combine(fecha, datetime.min.time())
    return fecha


def crear_devolucion(
    *,
    db,
    fecha,
    folio,
    cliente,
    direccion,
    motivo,
    zona,
    items,
    vendedor_id=None,
):
    # 1️⃣ Generar ID de negocio
    devolucion_id = str(uuid.uuid4())

    # 2️⃣ Normalizar fecha (ANTES de persistir)
    fecha = _normalizar_fecha(fecha)

    # 3️⃣ Construir dominio desde datos de UI
    devol = devolucion_from_ui(
        devolucion_id=devolucion_id,
        folio=folio,
        cliente=cliente,
        direccion=direccion,
        motivo=motivo,
        zona=zona,
        vendedor_id=vendedor_id,
        articulos=items,
    )

    # 4️⃣ Validar reglas de negocio (dominio)
    devol.validar()

    # 5️⃣ Mapear dominio → estructura persistible
    data = devolucion_to_persistence(devol)

    # 6️⃣ Persistir en DB
    db.insertar_devolucion(
        devolucion_id=devol.id,
        fecha=fecha,
        **data
    )

    # 7️⃣ Retornar ID generado
    return devol.id
