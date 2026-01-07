from os import getenv

from db.mongo.client import MongoClientProvider
from db.mongo.repos.productos_repo import ProductosRepo
from services.productos_service import ProductosService


# ─────────────────────────────────────────────
# DB BASE
# ─────────────────────────────────────────────
def get_db():
    """
    Devuelve el proveedor Mongo (infraestructura).
    """
    uri = getenv("MONGO_URI")
    db_name = getenv("MONGO_DB")

    if not uri or not db_name:
        raise RuntimeError(
            "Variables de entorno MONGO_URI y MONGO_DB no definidas"
        )

    return MongoClientProvider(uri, db_name)


# ─────────────────────────────────────────────
# REPOSITORIOS
# ─────────────────────────────────────────────
def get_productos_repo():
    """
    Devuelve el repositorio de productos.
    """
    db_provider = get_db()
    return ProductosRepo(db_provider._db)


# ─────────────────────────────────────────────
# SERVICES
# ─────────────────────────────────────────────
def get_productos_service():
    """
    Devuelve el servicio de productos correctamente cableado.
    """
    repo = get_productos_repo()
    return ProductosService(repo)
