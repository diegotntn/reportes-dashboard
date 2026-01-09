from dataclasses import dataclass


@dataclass
class Vendedor:
    id: str
    nombre: str
    activo: bool = True

    def validar_nombre(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Nombre del vendedor obligatorio.")

    def validar_activo(self):
        if not self.activo:
            raise ValueError("Vendedor inactivo.")

    def desactivar(self):
        self.activo = False
