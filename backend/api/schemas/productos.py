from pydantic import BaseModel
from typing import Optional


# ─────────────────────────
# RESPUESTAS
# ─────────────────────────

class ProductoOut(BaseModel):
    clave: str
    nombre: str
    precio: Optional[float] = None
    stock: Optional[int] = None

    class Config:
        from_attributes = True
