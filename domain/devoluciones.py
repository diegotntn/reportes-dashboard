# domain/devoluciones.py
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Articulo:
    nombre: str
    codigo: str
    pasillo: str
    cantidad: int
    unitario: float

    @property
    def total(self) -> float:
        return round(self.cantidad * self.unitario, 2)

    @classmethod
    def from_dict(cls, data: dict) -> "Articulo":
        return cls(
            nombre=data["nombre"],
            codigo=data["codigo"],
            pasillo=data["pasillo"],
            cantidad=int(data["cantidad"]),
            unitario=float(data["unitario"]),
        )


@dataclass
class Devolucion:
    id: str
    folio: str
    cliente: str
    direccion: str
    motivo: str
    zona: str
    articulos: List[Articulo] = field(default_factory=list)
    vendedor_id: Optional[str] = None
    estatus: str = "pendiente"

    def total(self) -> float:
        return round(sum(a.total for a in self.articulos), 2)

    def validar(self):
        if not self.folio:
            raise ValueError("La devolución debe tener folio.")
        if not self.articulos:
            raise ValueError("Debe contener al menos un artículo.")
        if self.total() <= 0:
            raise ValueError("El total debe ser mayor a cero.")

    def cambiar_estatus(self, nuevo: str):
        permitidos = {"pendiente", "aprobada", "rechazada"}
        if nuevo not in permitidos:
            raise ValueError(f"Estatus inválido: {nuevo}")
        self.estatus = nuevo
