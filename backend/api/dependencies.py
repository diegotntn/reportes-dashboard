"""
Dependencias de la API (SOLO REPORTES).

RESPONSABILIDAD:
- Proveer acceso a MongoDB (solo lectura)
- Inyectar el MongoClientProvider correcto
- Construir Queries analíticas
- Inyectar el Service de reportes

NO HACE:
- CRUD
- Escritura de datos
- Lógica de negocio
- Agregaciones analíticas

GRAFO CORRECTO:
MongoClientProvider → ReportesQueries → ReportesService
"""

# ─────────────────────────────────────────
# DB PROVIDER (SOLO LECTURA)
# ─────────────────────────────────────────
from backend.db.factory import get_db
from backend.db.mongo.client import MongoClientProvider


def get_database() -> MongoClientProvider:
    """
    Devuelve el proveedor Mongo en modo SOLO LECTURA.
    """
    print("\n🔗 [dependencies] get_database()")
    provider = get_db()
    print("   ✔ MongoClientProvider listo")
    return provider


# ─────────────────────────────────────────
# QUERIES ANALÍTICAS
# ─────────────────────────────────────────
from backend.db.mongo.reportes.queries import ReportesQueries


def get_reportes_queries() -> ReportesQueries:
    """
    Construye las queries analíticas de reportes.

    ⚠️ CLAVE:
    - Se inyecta el MongoClientProvider COMPLETO
    - NO se pasa una colección suelta
    """
    print("\n🧩 [dependencies] get_reportes_queries()")

    provider = get_database()

    queries = ReportesQueries(provider)

    print("   ✔ ReportesQueries creado correctamente")
    return queries


# ─────────────────────────────────────────
# SERVICE (ORQUESTADOR)
# ─────────────────────────────────────────
from backend.services.reportes.service import ReportesService


def get_reportes_service() -> ReportesService:
    """
    Proveedor del servicio de reportes.

    Inyecta:
    - ReportesQueries (lectura Mongo)
    """
    print("\n🧠 [dependencies] get_reportes_service()")

    queries = get_reportes_queries()

    service = ReportesService(reportes_queries=queries)

    print("   ✔ ReportesService listo")
    return service
