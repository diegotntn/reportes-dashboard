from fastapi import FastAPI

from backend.api.routes import (
    productos,
    devoluciones,
    personal,
    reportes,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ReporteSurtido API",
        version="1.0.0",
    )

    app.include_router(productos.router, prefix="/productos", tags=["Productos"])
    app.include_router(devoluciones.router, prefix="/devoluciones", tags=["Devoluciones"])
    app.include_router(personal.router, prefix="/personal", tags=["Personal"])
    app.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])

    return app


# 👇 ESTO ES LO QUE Uvicorn NECESITA
app = create_app()
