from pydantic import BaseModel
from typing import List, Optional


# ─────────────────────────
# ARTÍCULOS
# ─────────────────────────

class ArticuloIn(BaseModel):
    nombre: str
    codigo: str
    pasillo: str
    cantidad: int
    unitario: float


class ArticuloOut(ArticuloIn):
    total: float


# ─────────────────────────
# DEVOLUCIÓN (REQUEST)
# ─────────────────────────

class DevolucionCreate(BaseModel):
    fecha: str
    folio: str
    cliente: str
    direccion: str
    motivo: str
    zona: str
    items: List[ArticuloIn]
    vendedor_id: Optional[str] = None


class DevolucionUpdate(BaseModel):
    fecha: Optional[str] = None
    folio: Optional[str] = None
    cliente: Optional[str] = None
    direccion: Optional[str] = None
    motivo: Optional[str] = None
    zona: Optional[str] = None
    items: Optional[List[ArticuloIn]] = None


# ─────────────────────────
# DEVOLUCIÓN (RESPONSE)
# ─────────────────────────

class DevolucionOut(BaseModel):
    id: str
    fecha: str
    folio: str
    cliente: str
    direccion: str
    motivo: str
    zona: str
    estatus: str
    vendedor_id: Optional[str]
    items: List[ArticuloOut]
    total: float
