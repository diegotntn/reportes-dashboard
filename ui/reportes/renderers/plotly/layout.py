"""
layout.py

Este archivo define el DISEÑO VISUAL GLOBAL para todos los renderers Plotly
del sistema. Funciona como la fuente única de verdad para colores,
tipografías y tamaños, garantizando coherencia visual tipo
Power BI / Tableau en todo el dashboard.

REGLAS:
- Aquí NO se dibuja nada.
- Aquí NO se manejan datos.
- Aquí SOLO se definen constantes visuales reutilizables.
"""

from typing import Dict, List

# ─────────────────────────────────────────────
# 🎨 PALETAS DE COLOR
# ─────────────────────────────────────────────

PALETTE: Dict[str, str] = {
    # Colores principales
    "primary": "#2563EB",     # Azul corporativo
    "secondary": "#64748B",   # Gris neutro
    "accent": "#8B5CF6",      # Acento visual

    # Estados
    "success": "#22C55E",     # Verde positivo
    "warning": "#F59E0B",     # Amarillo advertencia
    "danger": "#EF4444",      # Rojo negativo

    # Fondos
    "background": "#0F172A",  # Fondo principal (dark)
    "surface": "#020617",     # Tarjetas / paneles
    "border": "#1E293B",      # Líneas y divisores
}

# Paleta categórica para gráficas (rotativa)
CATEGORY_COLORS: List[str] = [
    "#2563EB", "#22C55E", "#F59E0B", "#EF4444",
    "#8B5CF6", "#14B8A6", "#E11D48", "#0EA5E9"
]

# ─────────────────────────────────────────────
# 🔠 TIPOGRAFÍAS
# ─────────────────────────────────────────────

FONTS: Dict[str, Dict[str, any]] = {
    "base": {
        "family": "Segoe UI, Roboto, Arial",
        "size": 12,
        "color": "#E5E7EB"
    },
    "title": {
        "family": "Segoe UI, Roboto, Arial",
        "size": 16,
        "color": "#F9FAFB"
    },
    "kpi": {
        "family": "Segoe UI, Roboto, Arial",
        "size": 42,
        "color": "#F9FAFB"
    },
    "small": {
        "family": "Segoe UI, Roboto, Arial",
        "size": 10,
        "color": "#CBD5E1"
    }
}

# ─────────────────────────────────────────────
# 📐 TAMAÑOS Y ESPACIADO
# ─────────────────────────────────────────────

SIZES: Dict[str, int] = {
    "chart_height_sm": 240,
    "chart_height_md": 320,
    "chart_height_lg": 420,

    "kpi_height": 180,
    "card_padding": 16,
    "section_gap": 24
}

# ─────────────────────────────────────────────
# 🧭 LAYOUT PRESETS
# ─────────────────────────────────────────────

LAYOUT_PRESETS: Dict[str, Dict[str, any]] = {
    "dashboard": {
        "margin": dict(l=32, r=32, t=48, b=32),
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "hovermode": "closest"
    },
    "card": {
        "margin": dict(l=20, r=20, t=40, b=20)
    }
}

# ─────────────────────────────────────────────
# 🎯 UTILIDADES VISUALES
# ─────────────────────────────────────────────

def get_palette_color(key: str, default: str = "#2563EB") -> str:
    """
    Obtiene un color de la paleta por clave.

    Args:
        key (str):
            Clave del color (primary, success, danger, etc.).

        default (str):
            Color por defecto si la clave no existe.

    Returns:
        str:
            Código hexadecimal del color.
    """
    return PALETTE.get(key, default)


def get_category_color(index: int) -> str:
    """
    Obtiene un color categórico de forma cíclica.

    Args:
        index (int):
            Índice de la categoría.

    Returns:
        str:
            Código hexadecimal del color.
    """
    return CATEGORY_COLORS[index % len(CATEGORY_COLORS)]
