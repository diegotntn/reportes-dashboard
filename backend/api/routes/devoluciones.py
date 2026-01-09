"""
Rutas API para devoluciones.

Responsabilidad:
- Traducir HTTP → DevolucionesService
- Manejar errores de validación
- Devolver JSON listo para frontend

NO contiene:
- Lógica de negocio
- Acceso a Mongo
- pandas
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from backend.api.dependencies import get_devoluciones_service
from backend.services.devoluciones.service import DevolucionesService

router = APIRouter()
