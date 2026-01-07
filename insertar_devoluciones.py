import random
from datetime import date, timedelta
from dotenv import load_dotenv
import os

from services.devoluciones.commands.crear_devolucion import crear_devolucion
from db.mongo.client import MongoClientProvider  # ajusta si tu wrapper tiene otro nombre

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
load_dotenv()

db = MongoClientProvider(
    uri=os.getenv("MONGO_URI"),
    db_name=os.getenv("MONGO_DB")
)

ZONAS = [
    "Z11","Z12","Z13","Z14","Z15",
    "Z17","Z18","Z19","Z20","Z21",
    "Z22","Z23","Z27","Z28",
]

# ─────────────────────────────
# HELPERS
# ─────────────────────────────
def zona_random():
    return random.choice(ZONAS)


def fecha_random_noviembre_2025():
    inicio = date(2025, 11, 1)
    fin = date(2025, 11, 30)
    delta = (fin - inicio).days
    return inicio + timedelta(days=random.randint(0, delta))


def pasillo_from_linea(linea: str):
    try:
        n = int(linea[0])
    except Exception:
        return "P4"
    return f"P{n}" if n <= 3 else "P4"


# ─────────────────────────────
# CATÁLOGO DE EJEMPLO
# ─────────────────────────────
CATALOGO = [
    {
        "codigo": "7501125105104",
        "nombre": "TOBRAMICINA/DEXAMETASONA 3MG/1MG/1ML GTS OFT",
        "linea": "3CT-01",
        "precio": 156.24,
    },
    {
        "codigo": "7501008490012",
        "nombre": "PARACETAMOL 500MG TAB C/20",
        "linea": "1CT-01",
        "precio": 32.50,
    },
    {
        "codigo": "7501125108888",
        "nombre": "IBUPROFENO 400MG TAB C/30",
        "linea": "2CT-01",
        "precio": 48.00,
    },
    {
        "codigo": "7501031313131",
        "nombre": "AMOXICILINA 500MG CAP C/12",
        "linea": "2CT-01",
        "precio": 14.99,
    },
    {
        "codigo": "7502222333344",
        "nombre": "SUEROX MORA AZUL 630ML",
        "linea": "4CT-01",
        "precio": 15.86,
    },
]

CLIENTES = [
    "FARMACIAS YA VAZ (SUC. TLAXCALA)",
    "FARMACIAS YA VAZ (SUC. PRADOS)",
    "FARMACIAS YA VAZ (SUC. ZARAGOZA 2)",
    "CLIENTE MOSTRADOR - R",
    "MARIA HERNANDEZ LOPEZ - R",
    "JOSE PEREZ RAMIREZ - R",
]

# ─────────────────────────────
# LIMPIEZA (OPCIONAL)
# ─────────────────────────────
print("🧹 (Opcional) Limpiando devoluciones existentes…")
db._db.devoluciones.delete_many({})

# ─────────────────────────────
# CARGA MASIVA (50 DEVOLUCIONES)
# ─────────────────────────────
print("📥 Insertando 50 devoluciones de noviembre…")

for i in range(50):
    fecha = fecha_random_noviembre_2025()
    cliente = random.choice(CLIENTES)
    zona = zona_random()

    # Generar artículos (1 a 3 por devolución)
    items = []
    for art in random.sample(CATALOGO, random.randint(1, 3)):
        cantidad = random.randint(1, 5)
        items.append({
            "codigo": art["codigo"],
            "nombre": art["nombre"],
            "linea": art["linea"],
            "pasillo": pasillo_from_linea(art["linea"]),
            "cantidad": cantidad,
            "precio": art["precio"],
            "subtotal": round(cantidad * art["precio"], 2),
        })

    crear_devolucion(
        db=db,
        fecha=fecha,                         # 👈 date → command lo normaliza
        folio=f"AUTO-NOV-{i+1:03d}",
        cliente=cliente,
        direccion=cliente,
        motivo="caducidad",
        zona=zona,
        items=items,
        vendedor_id=None,
    )

print("✅ 50 devoluciones de noviembre insertadas correctamente.")
