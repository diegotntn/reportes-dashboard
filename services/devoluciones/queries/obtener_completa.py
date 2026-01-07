"""
Query: obtener devolución completa.

RESPONSABILIDAD:
- Obtener encabezado + artículos
- Usado exclusivamente para edición

NO HACE:
- Validaciones
- Transformaciones
"""

def obtener_completa(db, devolucion_id: str):
    """
    Devuelve la devolución completa desde DB.
    """

    if not devolucion_id:
        return None

    return db.get_devolucion_completa(devolucion_id)
