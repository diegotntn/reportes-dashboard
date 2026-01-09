"""
Query: obtener devolución completa.

RESPONSABILIDAD:
- Obtener encabezado + artículos
- Usado exclusivamente para edición

NO HACE:
- Validaciones de dominio
- Transformaciones complejas
"""

def obtener_completa(*, repo, devolucion_id: str):
    """
    Devuelve la devolución completa desde el repositorio.

    Parámetros
    ----------
    repo : DevolucionesRepo
        Repositorio de devoluciones
    devolucion_id : str
        ID de la devolución
    """

    if not devolucion_id:
        return None

    # Acceso único vía repositorio
    doc = repo.collection.find_one({"_id": devolucion_id})

    if not doc:
        return None

    # Normalización mínima para la API
    doc["id"] = doc.pop("_id")

    if "fecha" in doc and hasattr(doc["fecha"], "date"):
        doc["fecha"] = doc["fecha"].date().isoformat()

    return doc
