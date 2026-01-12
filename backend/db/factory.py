import os
from pathlib import Path
from dotenv import load_dotenv

from backend.db.mongo.client import MongoClientProvider


# ─────────────────────────────────────────────
# 🔑 CARGA EXPLÍCITA DEL .env (RUTA ABSOLUTA)
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ─────────────────────────────────────────────
# DB PROVIDER (SOLO LECTURA)
# ─────────────────────────────────────────────
def get_db() -> MongoClientProvider:
    """
    Devuelve el proveedor Mongo para consultas de REPORTES.
    
    ❌ No expone repos
    ❌ No permite escritura
    ✅ Solo acceso a colecciones
    """
    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB")

    if not uri or not db_name:
        raise RuntimeError(
            "Variables de entorno MONGO_URI y MONGO_DB no definidas"
        )

    return MongoClientProvider(uri, db_name)
