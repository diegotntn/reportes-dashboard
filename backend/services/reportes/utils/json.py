import math
import numpy as np


def limpiar_json(obj):
    """
    Convierte NaN / inf / -inf en None recursivamente
    para que JSON sea válido.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj

    if isinstance(obj, np.generic):
        return limpiar_json(obj.item())

    if isinstance(obj, dict):
        return {k: limpiar_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [limpiar_json(v) for v in obj]

    return obj
