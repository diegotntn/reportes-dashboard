# utils/helpers.py
from datetime import date


# ─────────────────────────────────────────────
# FORMATO / CASTING
# ─────────────────────────────────────────────

def money(x) -> str:
    """
    Formatea un número como moneda.
    """
    try:
        return f"${float(x):,.2f}"
    except Exception:
        return "$0.00"


def ffloat(s) -> float:
    """
    Convierte string a float limpiando comas y espacios.
    """
    try:
        return float(str(s).strip().replace(",", ""))
    except Exception:
        return 0.0


def fint(s) -> int:
    """
    Convierte string a int.
    """
    try:
        return int(str(s).strip())
    except Exception:
        return 0


# ─────────────────────────────────────────────
# FECHAS
# ─────────────────────────────────────────────

def today_str() -> str:
    """
    Devuelve la fecha actual en formato ISO (YYYY-MM-DD).
    """
    return date.today().isoformat()


def first_day_month(d: date) -> date:
    """
    Devuelve el primer día del mes de una fecha dada.
    """
    return d.replace(day=1)


# ─────────────────────────────────────────────
# PRODUCTOS / NEGOCIO
# ─────────────────────────────────────────────

def producto_surtible(producto: dict) -> bool:
    """
    Determina si un producto es surtible.

    Regla:
    - lcd4 debe existir y no ser None
    """
    if not producto:
        return False
    return producto.get("lcd4") is not None


def normalizar_codigo(codigo: str) -> str:
    """
    Normaliza el código del producto para búsqueda.
    """
    if not codigo:
        return ""
    return str(codigo).strip().upper()


def normalizar_texto_busqueda(texto: str) -> str:
    """
    Normaliza texto para búsquedas por código o nombre.
    """
    if not texto:
        return ""
    return (
        str(texto)
        .strip()
        .upper()
        .replace("  ", " ")
    )


def label_producto(producto: dict) -> str:
    """
    Etiqueta legible para autocompletado.
    """
    return f"{producto.get('clave','')} — {producto.get('nombre','')}"


# ─────────────────────────────────────────────
# UBICACIÓN / PASILLOS
# ─────────────────────────────────────────────

def pasillo_desde_linea(linea: str):
    """
    Obtiene el pasillo lógico a partir de la línea del producto.

    Reglas:
    - "PLUS MEDIC 1" → selección manual (retorna None)
    - Primer número encontrado define el pasillo
    - Pasillos >= 4 se agrupan como P4
    """
    if not linea:
        return None

    linea = str(linea).strip().upper()

    # Excepción: pasillo manual
    if linea == "PLUS MEDIC 1":
        return None

    # Buscar el primer dígito
    for char in linea:
        if char.isdigit():
            pasillo = int(char)
            break
    else:
        return None

    if pasillo >= 4:
        return "P4"

    return f"P{pasillo}"
