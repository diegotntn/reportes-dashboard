"""
Punto de entrada del backend ReporteSurtido.

RESPONSABILIDADES:
- Crear la aplicación FastAPI
- Configurar middlewares (CORS)
- Registrar rutas de la API (solo reportes)
- Exponer la app para Uvicorn

NO CONTIENE:
- Lógica de negocio
- Acceso a base de datos
- Validaciones de dominio
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import reportes


# ─────────────────────────────────────────
# CREACIÓN DE LA APLICACIÓN
# ─────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="ReporteSurtido · Dashboard API",
        description="API de solo lectura para reportes y visualización de gráficas",
        version="2.0.0",
    )

    # ─────────────────────────────────────────
    # CORS (FRONTEND WEB)
    # ─────────────────────────────────────────
    # Para desarrollo solamente
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permite todo (¡solo en dev!)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─────────────────────────────────────────
    # REGISTRO DE RUTAS
    # ─────────────────────────────────────────
    app.include_router(
        reportes.router,
        prefix="/api/reportes",
        tags=["Reportes"],
    )

    # ─────────────────────────────────────────
    # HEALTH CHECK
    # ─────────────────────────────────────────
    @app.get("/api/health", tags=["Health"])
    def health_check():
        return {"status": "ok"}

    return app


# ─────────────────────────────────────────
# EXPOSICIÓN PARA UVICORN
# ─────────────────────────────────────────
app = create_app()
