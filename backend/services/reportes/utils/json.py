import math
import numpy as np
from datetime import datetime, date
from decimal import Decimal

try:
    import pandas as pd
except ImportError:
    pd = None


def limpiar_json(obj):
    """
    Limpia y serializa datos para JSON sin romper
    reportes existentes.

    - Convierte NaN / inf / -inf → None
    - Soporta numpy scalar
    - Soporta datetime / date
    - Soporta pandas Timestamp / Period (solo si pandas existe)
    - Soporta Decimal
    """

    # ───────── floats problemáticos ─────────
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    # ───────── numpy scalar ─────────
    if isinstance(obj, np.generic):
        return limpiar_json(obj.item())

    # ───────── datetime estándar ─────────
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # ───────── pandas (solo si existe) ─────────
    if pd:
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, pd.Period):
            return str(obj)

    # ───────── decimal ─────────
    if isinstance(obj, Decimal):
        return float(obj)

    # ───────── estructuras ─────────
    if isinstance(obj, dict):
        return {k: limpiar_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [limpiar_json(v) for v in obj]

    return obj
