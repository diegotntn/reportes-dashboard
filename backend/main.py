"""
Punto de entrada del backend ReporteSurtido.

RESPONSABILIDADES:
- Crear la aplicación FastAPI
- Configurar middlewares (CORS)
- Registrar rutas de la API
- Exponer la app para Uvicorn

NO CONTIENE:
- Lógica de negocio
- Acceso a base de datos
- Validaciones de dominio
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import (
    productos,
    devoluciones,
    personal,
    reportes,
)

# ─────────────────────────────────────────
# CREACIÓN DE LA APLICACIÓN
# ─────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        title="ReporteSurtido API",
        description="Backend para reportes, devoluciones y productos",
        version="1.0.0",
    )

    # ─────────────────────────────────────────
    # CORS (FRONTEND WEB)
    # ─────────────────────────────────────────
    # ⚠️ NO usar "*" cuando allow_credentials=True
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5500",
            "http://127.0.0.1:5500",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─────────────────────────────────────────
    # REGISTRO DE RUTAS (PREFIJO /api)
    # ─────────────────────────────────────────
    app.include_router(
        productos.router,
        prefix="/api/productos",
        tags=["Productos"]
    )

    app.include_router(
        devoluciones.router,
        prefix="/api/devoluciones",
        tags=["Devoluciones"]
    )

    app.include_router(
        personal.router,
        prefix="/api/personal",
        tags=["Personal"]
    )

    app.include_router(
        reportes.router,
        prefix="/api/reportes",
        tags=["Reportes"]
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
