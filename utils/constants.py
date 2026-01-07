import os

# ───────────────── RUTAS Y BD ─────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "devoluciones.db")

# Motor de base de datos: "sqlite" | "mongo"
DB_ENGINE = "sqlite"

# ───────────────── MONGO ─────────────────
MONGO_URI = "mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net"
MONGO_DB = "plusmedic"

# ───────────────── ZONAS ─────────────────
# Catálogo REAL de zonas (ventas / vendedores)
# Fuente: listado oficial proporcionado

ZONA_PREFIX = "Z"

ZONAS = [
    "Z11",
    "Z12",
    "Z13",
    "Z14",
    "Z15",
    "Z17",
    "Z18",
    "Z19",
    "Z20",
    "Z21",
    "Z22",
    "Z23",
    "Z27",
    "Z28",
]

# ───────────────── MOTIVOS DE DEVOLUCIÓN ─────────────────
MOTIVOS = [
    "caducidad",
    "cambio de articulo",
    "mal estado",
    "captura",
    "precio",
    "faltante",
    "cliente",
]

# ───────────────── PASILLOS ─────────────────
PASILLOS = [
    "P1",
    "P2",
    "P3",
    "P4",
]

# ───────────────── UI ─────────────────
APP_TITLE = "Sistema de Devoluciones"
WINDOW_SIZE = "1250x760"
WINDOW_MIN_SIZE = (1100, 680)
