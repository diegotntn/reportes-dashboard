import os
from pathlib import Path
from dotenv import load_dotenv

from backend.db.mongo.client import MongoClientProvider
from backend.db.mongo.repos.productos_repo import ProductosRepo
from backend.services.productos_service import ProductosService


# ─────────────────────────────────────────────
# 🔑 CARGA EXPLÍCITA DEL .env (RUTA ABSOLUTA)
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ─────────────────────────────────────────────
# DB BASE
# ─────────────────────────────────────────────
def get_db():
    """
    Devuelve el proveedor Mongo (infraestructura).
    """
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")

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
