from dataclasses import dataclass


@dataclass
class Persona:
    id: str
    nombre: str
    activo: bool = True

    def validar_nombre(self):
        if not self.nombre or not self.nombre.strip():
            raise ValueError("Nombre requerido")

    def renombrar(self, nuevo_nombre: str):
        if not nuevo_nombre or not nuevo_nombre.strip():
            raise ValueError("Nombre requerido")
        self.nombre = nuevo_nombre.strip()

    def desactivar(self):
        self.activo = False
