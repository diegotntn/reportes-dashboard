"""
Agregaciones puras para reportes.

Este paquete expone funciones de agregación
que operan sobre DataFrames normalizados.
"""

from .general import agrupa_general
from .zona import agrupa_por_zona
from .pasillo import agrupa_por_pasillo
from .tabla import tabla_final

__all__ = [
    "agrupa_general",
    "agrupa_por_zona",
    "agrupa_por_pasillo",
    "tabla_final",
]
