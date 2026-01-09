"""
Command: eliminar_devolucion

Elimina una devolución.

RESPONSABILIDAD:
- Eliminar una devolución existente

NO HACE:
- Validaciones de dominio complejas
- Acceso directo a MongoDB
"""

def eliminar_devolucion(
    *,
    repo,
    devolucion_id: str,
):
    """
    Elimina una devolución por ID.
    """

    if not devolucion_id:
        raise ValueError("Devolución no especificada.")

    repo.eliminar(devolucion_id)

    return True
