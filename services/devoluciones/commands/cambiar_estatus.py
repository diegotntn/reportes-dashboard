"""
Command: cambiar_estatus
Cambia el estatus de una devolución.
"""

from domain.devoluciones import Devolucion


def cambiar_estatus(
    *,
    db,
    devolucion_id,
    nuevo_estatus,
):
    if not devolucion_id:
        raise ValueError("Devolución no especificada.")

    # 1️⃣ Dominio mínimo para validar transición
    devol = Devolucion(
        id=devolucion_id,
        folio="tmp",
        cliente="tmp",
        direccion="tmp",
        motivo="tmp",
        zona="tmp",
    )

    # 2️⃣ Validar cambio de estatus
    devol.cambiar_estatus(nuevo_estatus)

    # 3️⃣ Persistir
    db.actualizar_devolucion(
        devolucion_id,
        estatus=nuevo_estatus,
    )
