"""
Command: eliminar_devolucion
Elimina una devolución.
"""


def eliminar_devolucion(
    *,
    db,
    devolucion_id,
):
    if not devolucion_id:
        raise ValueError("Devolución no especificada.")

    # Eliminación directa
    db.eliminar_devolucion(devolucion_id)
