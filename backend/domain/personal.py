from dataclasses import dataclass


@dataclass(frozen=True)
class Persona:
    """
    Persona (dimensión de análisis).

    MODELO DE LECTURA:
    - Describe a una persona en un contexto histórico
    - No valida
    - No muta
    - No contiene reglas de negocio
    """
    id: str
    nombre: str
    activo: bool
