def money(valor) -> str:
    """
    Formatea un número como moneda MXN.
    """
    try:
        return f"${float(valor):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"
