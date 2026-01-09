"""
Helpers de texto usados en la capa de servicios.

REGLAS:
- No depende de DB
- No depende de API (FastAPI)
- No depende de UI
- Solo transformación y normalización de texto
"""


def normalizar_texto_busqueda(texto: str) -> str:
    """
    Normaliza texto para búsquedas flexibles.

    Reglas aplicadas:
    - Convierte a string
    - Elimina espacios al inicio y final
    - Convierte a minúsculas

    Ejemplos:
    - "  Paracetamol  " → "paracetamol"
    - "ABC-123" → "abc-123"
    """
    if texto is None:
        return ""

    return str(texto).strip().lower()
