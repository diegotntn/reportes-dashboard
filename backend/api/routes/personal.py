"""
Rutas API para personal operativo y asignaciones.

Responsabilidad:
- Traducir HTTP → PersonalService
- Manejar errores de validación
- Devolver JSON listo para frontend

NO contiene:
- Lógica de negocio
- Acceso directo a Mongo
- pandas
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

from backend.api.dependencies import get_personal_service
from backend.services.personal_service import PersonalService

router = APIRouter()
