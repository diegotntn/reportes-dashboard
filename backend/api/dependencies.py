"""
Dependencias de la API (SOLO REPORTES).

RESPONSABILIDAD:
- Proveer acceso a la base de datos (Mongo, solo lectura)
- Obtener la colección correcta
- Construir queries analíticas
- Inyectar el servicio de reportes

NO HACE:
- CRUD
- Escritura de datos
- Lógica de negocio
- Lógica de agregación

Aquí vive ÚNICAMENTE la composición del grafo:
MongoClientProvider → Collection → Queries → Service
"""

# ─────────────────────────────────────────
# DB PROVIDER (SOLO LECTURA)
# ─────────────────────────────────────────
from backend.db.factory import get_db
from backend.db.mongo.client import MongoClientProvider


def get_database() -> MongoClientProvider:
    """
    Devuelve el proveedor de base de datos.
    (MongoClientProvider en modo lectura)
    """
    return get_db()


# ─────────────────────────────────────────
# QUERIES ANALÍTICAS
# ─────────────────────────────────────────
from backend.db.mongo.reportes.queries import ReportesQueries


def get_reportes_queries() -> ReportesQueries:
    """
    Construye el objeto de queries de reportes.

    IMPORTANTE:
    - Aquí se obtiene la colección
    - NO se pasa el provider completo
    """
    db = get_database()

    # 🔑 COLECCIÓN REAL (NO el provider)
    collection = db.get_collection("devoluciones")

    return ReportesQueries(collection)


# ─────────────────────────────────────────
# SERVICES (ORQUESTADOR)
# ─────────────────────────────────────────
from backend.services.reportes.service import ReportesService


def get_reportes_service() -> ReportesService:
    """
    Proveedor del servicio de reportes.

    Inyecta:
    - ReportesQueries (lectura Mongo)
    """
    queries = get_reportes_queries()
    return ReportesService(reportes_queries=queries)
