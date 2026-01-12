from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Producto:
    """
    Producto (dimensión de análisis).

    MODELO DE LECTURA:
    - Describe un producto tal como existe en los datos históricos
    - No valida
    - No normaliza
    - No muta
    """
    clave: str
    nombre: str
    linea: str
    lcd4: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        """
        Construye un Producto desde un dict (lectura).
        No valida reglas de negocio.
        """
        return cls(
            clave=str(data.get("clave", "")),
            nombre=str(data.get("nombre", "")),
            linea=str(data.get("linea", "")),
            lcd4=(
                float(data["lcd4"])
                if data.get("lcd4") is not None
                else None
            ),
        )

    def to_dict(self) -> dict:
        """
        Devuelve una representación serializable y estable.
        """
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "linea": self.linea,
            "lcd4": self.lcd4,
        }
