# domain/devoluciones.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class Articulo:
    """
    Artículo devuelto (modelo de lectura).

    Representa un dato histórico.
    NO valida, NO calcula estado, NO muta.
    """
    nombre: str
    codigo: str
    pasillo: str
    cantidad: int
    unitario: float

    @property
    def total(self) -> float:
        """
        Total del artículo (cálculo derivado, sin efectos secundarios).
        """
        return round(self.cantidad * self.unitario, 2)

    @classmethod
    def from_dict(cls, data: dict) -> "Articulo":
        """
        Crea un Articulo desde un dict (lectura).
        """
        return cls(
            nombre=data.get("nombre", ""),
            codigo=data.get("codigo", ""),
            pasillo=data.get("pasillo", ""),
            cantidad=int(data.get("cantidad", 0)),
            unitario=float(data.get("unitario", 0.0)),
        )


@dataclass(frozen=True)
class Devolucion:
    """
    Devolución (evento histórico).

    MODELO DE LECTURA:
    - Describe lo que ocurrió
    - No valida
    - No cambia estatus
    - No impone reglas de negocio
    """
    id: str
    folio: str
    cliente: str
    direccion: str
    motivo: str
    zona: str
    articulos: List[Articulo]
    vendedor_id: Optional[str]
    estatus: str

    @property
    def total(self) -> float:
        """
        Total de la devolución (derivado).
        """
        return round(sum(a.total for a in self.articulos), 2)

    @classmethod
    def from_dict(cls, data: dict) -> "Devolucion":
        """
        Construye una Devolución desde un dict Mongo.
        """
        articulos = [
            Articulo.from_dict(a)
            for a in data.get("articulos", [])
        ]

        return cls(
            id=str(data.get("_id")),
            folio=data.get("folio", ""),
            cliente=data.get("cliente", ""),
            direccion=data.get("direccion", ""),
            motivo=data.get("motivo", ""),
            zona=data.get("zona", ""),
            articulos=articulos,
            vendedor_id=data.get("vendedor_id"),
            estatus=data.get("estatus", ""),
        )
