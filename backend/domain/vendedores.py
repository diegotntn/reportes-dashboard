from dataclasses import dataclass


@dataclass(frozen=True)
class Vendedor:
    """
    Vendedor (dimensión de análisis).

    MODELO DE LECTURA:
    - Describe a un vendedor en un momento histórico
    - No valida
    - No muta
    - No contiene reglas de negocio
    """
    id: str
    nombre: str
    activo: bool
