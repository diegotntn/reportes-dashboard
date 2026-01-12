def map_periodo(periodo: str) -> str:
    """
    Normaliza el periodo solicitado por el frontend.

    Acepta:
    - Dia / día / dia
    - Semana
    - Mes
    - Año / Anio

    Devuelve:
    - 'dia'
    - 'semana'
    - 'mes'
    - 'anio'
    """

    if not periodo:
        return "mes"

    p = periodo.strip().lower()

    if p in ("dia", "día"):
        return "dia"

    if p == "semana":
        return "semana"

    if p == "anio" or p == "año":
        return "anio"

    return "mes"
