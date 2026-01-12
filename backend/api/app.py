from fastapi import FastAPI

from backend.api.routes import reportes


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReporteSurtido · Reportes",
        version="2.0.0",
    )

    # ─────────────────────────────────────────
    # ÚNICA RUTA DE LA APLICACIÓN
    # ─────────────────────────────────────────
    app.include_router(
        reportes.router,
        prefix="/reportes",
        tags=["Reportes"],
    )

    return app


# 👇 ESTO ES LO QUE Uvicorn NECESITA
app = create_app()
