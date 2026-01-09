"""
Rutas API para productos.

Responsabilidad:
- Recibir peticiones HTTP
- Delegar a ProductosService
- Devolver JSON al frontend

NO contiene:
- Lógica de negocio
- Acceso a Mongo
"""

from fastapi import APIRouter, Depends, Query, HTTPException

from backend.api.dependencies import get_productos_service
from backend.services.productos_service import ProductosService

router = APIRouter()


# ─────────────────────────────────────────
# BUSCAR PRODUCTOS (AUTOCOMPLETE)
# ─────────────────────────────────────────
@router.get("/buscar")
def buscar_productos(
    q: str = Query(
        ...,
        min_length=2,
        description="Texto para buscar por clave o nombre"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Número máximo de resultados"
    ),
    service: ProductosService = Depends(get_productos_service),
):
    """
    Busca productos por coincidencia parcial en clave o nombre.
    Pensado para autocompletado en formularios.
    """
    return service.buscar(q, limit)


# ─────────────────────────────────────────
# OBTENER PRODUCTO POR CLAVE EXACTA
# ─────────────────────────────────────────
@router.get("/{clave}")
def obtener_producto(
    clave: str,
    service: ProductosService = Depends(get_productos_service),
):
    """
    Obtiene un producto por su clave exacta.
    """
    producto = service.obtener_por_clave(clave)

    if producto is None:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto
