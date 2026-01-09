"""
Dependencias de la API.

RESPONSABILIDAD:
- Crear proveedores de base de datos
- Crear repositorios
- Crear queries especializadas
- Inyectar services correctamente cableados

NOTA:
FastAPI solo usa Depends().
Aquí vive TODA la composición real de objetos.
"""

# ─────────────────────────────────────────
# DB PROVIDER
# ─────────────────────────────────────────
from backend.db.factory import get_db


def get_database():
    """
    Devuelve el proveedor de base de datos (MongoClientProvider).
    """
    return get_db()


# ─────────────────────────────────────────
# REPOSITORIOS
# ─────────────────────────────────────────
from backend.db.mongo.repos.productos_repo import ProductosRepo
from backend.db.mongo.repos.devoluciones_repo import DevolucionesRepo
from backend.db.mongo.repos.personal_repo import PersonalRepo


# ─────────────────────────────────────────
# QUERIES ESPECIALIZADAS
# ─────────────────────────────────────────
from backend.db.mongo.reportes.queries import ReportesQueries


# ─────────────────────────────────────────
# SERVICES
# ─────────────────────────────────────────
from backend.services.productos_service import ProductosService
from backend.services.devoluciones.service import DevolucionesService
from backend.services.personal_service import PersonalService
from backend.services.reportes.service import ReportesService


# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────
def get_productos_service() -> ProductosService:
    db = get_database()

    productos_repo = ProductosRepo(db._db)

    return ProductosService(
        productos_repo=productos_repo
    )


# ─────────────────────────────────────────
# DEVOLUCIONES
# ─────────────────────────────────────────
def get_devoluciones_service() -> DevolucionesService:
    db = get_database()

    devoluciones_repo = DevolucionesRepo(db._db)
    reportes_queries = ReportesQueries(devoluciones_repo)

    return DevolucionesService(
        devoluciones_repo=devoluciones_repo,
        reportes_queries=reportes_queries,
    )


# ─────────────────────────────────────────
# PERSONAL
# ─────────────────────────────────────────
def get_personal_service() -> PersonalService:
    db = get_database()

    personal_repo = PersonalRepo(db._db)

    # ⚠️ PersonalService NO crea queries, se las inyectamos
    devoluciones_repo = DevolucionesRepo(db._db)
    reportes_queries = ReportesQueries(devoluciones_repo)

    return PersonalService(
        personal_repo=personal_repo,
        reportes_queries=reportes_queries,
    )


# ─────────────────────────────────────────
# REPORTES
# ─────────────────────────────────────────
def get_reportes_service() -> ReportesService:
    db = get_database()

    # Repo base (fuente de datos)
    devoluciones_repo = DevolucionesRepo(db._db)

    # Queries especializadas
    reportes_queries = ReportesQueries(devoluciones_repo)

    # PersonalService (dependencia obligatoria)
    personal_repo = PersonalRepo(db._db)
    personal_service = PersonalService(
        personal_repo=personal_repo
    )
    return ReportesService(
        reportes_queries=reportes_queries,
        personal_service=personal_service,
    )
