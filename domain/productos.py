from dataclasses import dataclass


@dataclass(frozen=True)
class Producto:
    clave: str
    nombre: str
    linea: str
    lcd4: float | None = None

    def validar(self):
        if not self.clave or not self.clave.strip():
            raise ValueError("Producto sin clave")
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Producto sin nombre")
        if not self.linea or not self.linea.strip():
            raise ValueError("Producto sin línea")

    @classmethod
    def from_dict(cls, data: dict) -> "Producto":
        if not data:
            raise ValueError("Producto inválido")

        prod = cls(
            clave=data.get("clave"),
            nombre=data.get("nombre"),
            linea=data.get("linea"),
            lcd4=data.get("lcd4"),
        )
        prod.validar()
        return prod

    def normalizado(self) -> dict:
        """
        Devuelve estructura estable para UI / services.
        """
        return {
            "clave": self.clave,
            "nombre": self.nombre,
            "linea": self.linea,
            "lcd4": self.lcd4 or 0.0,
        }
