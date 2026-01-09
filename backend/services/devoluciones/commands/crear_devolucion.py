import uuid
from datetime import datetime, date

from backend.domain.devoluciones import Devolucion
from backend.services.devoluciones.mappers.devolucion_mapper import (
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
    repo,
    fecha,
    folio,
    cliente,
    direccion,
    motivo,
    zona,
    items,
    vendedor_id=None,
):
    # 1️⃣ ID de negocio
    devolucion_id = str(uuid.uuid4())

    # 2️⃣ Normalizar fecha
    fecha = _normalizar_fecha(fecha)

    # 3️⃣ Dominio
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

    # 4️⃣ Validar reglas
    devol.validar()

    # 5️⃣ Mapear dominio → persistencia
    data = devolucion_to_persistence(devol)

    # ⚠️ OJO:
    # tu repo espera campos planos, no un dict genérico
    repo.insertar(
        devolucion_id=devolucion_id,
        fecha=fecha,
        folio=data["folio"],
        cliente=data["cliente"],
        direccion=data["direccion"],
        motivo=data["motivo"],
        zona=data["zona"],
        total=data["total"],
        articulos=data["articulos"],
        vendedor_id=data.get("vendedor_id"),
        estatus=data.get("estatus", "pendiente"),
    )

    return devolucion_id
