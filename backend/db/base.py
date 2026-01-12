from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from datetime import datetime


class BaseDB(ABC):
    """
    Contrato base para backends de datos (SOLO REPORTES).

    REGLAS:
    - NO escribe datos
    - NO conoce MongoDB, SQLite ni detalles de infraestructura
    - SOLO expone métodos de lectura y agregación
    - Devuelve estructuras serializables (dict / list)
    """

    # ─────────────────────────────
    # DEVOLUCIONES (LECTURA)
    # ─────────────────────────────
    @abstractmethod
    def find_devoluciones(
        self,
        *,
        filtro: Optional[Dict[str, Any]] = None,
        desde: Optional[datetime] = None,
        hasta: Optional[datetime] = None,
        vendedor_id: Optional[str] = None,
        estatus: Optional[str] = None,
    ) -> List[Dict]:
        """
        Devuelve devoluciones filtradas.

        - SOLO lectura
        - No transforma tipos
        """

    @abstractmethod
    def aggregate_devoluciones(
        self,
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Ejecuta un aggregate sobre devoluciones.
        """

    @abstractmethod
    def get_devolucion_completa(
        self,
        devolucion_id: Any
    ) -> Optional[Dict]:
        """
        Devuelve una devolución completa por ID.
        """

    # ─────────────────────────────
    # PERSONAL (LECTURA)
    # ─────────────────────────────
    @abstractmethod
    def listar_personal(
        self,
        *,
        solo_activos: bool = True
    ) -> List[Dict]:
        """
        Lista personal (lectura).
        """

    # ─────────────────────────────
    # ASIGNACIONES (LECTURA)
    # ─────────────────────────────
    @abstractmethod
    def listar_asignaciones(self) -> List[Dict]:
        """
        Lista asignaciones (lectura).
        """

    # ─────────────────────────────
    # VENDEDORES (LECTURA)
    # ─────────────────────────────
    @abstractmethod
    def listar_vendedores(
        self,
        *,
        solo_activos: bool = True
    ) -> List[Dict]:
        """
        Lista vendedores (lectura).
        """

    # ─────────────────────────────
    # GENÉRICO / SOPORTE
    # ─────────────────────────────
    @abstractmethod
    def close(self) -> None:
        """
        Cierra la conexión al backend de datos.
        """
