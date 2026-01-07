from abc import ABC, abstractmethod
from typing import Optional, Tuple
import pandas as pd


class BaseDB(ABC):
    """
    Contrato base para cualquier backend de datos del sistema.

    REGLAS:
    - NO conoce MongoDB ni SQLite
    - NO conoce UI
    - Devuelve estructuras que Services esperan (DataFrame)
    """

    # ───────────────── DEVOLUCIONES ─────────────────
    @abstractmethod
    def insertar_devolucion(
        self,
        *,
        devolucion_id: str,
        fecha,
        folio: str,
        cliente: str,
        direccion: str,
        motivo: str,
        zona: str,
        total: float,
        articulos: list[dict],
        vendedor_id: Optional[str] = None,
        estatus: str = "pendiente",
    ) -> None:
        """Inserta una devolución completa."""

    @abstractmethod
    def actualizar_devolucion(
        self,
        devolucion_id: str,
        *,
        fecha=None,
        folio=None,
        cliente=None,
        direccion=None,
        motivo=None,
        zona=None,
        items=None,
        estatus=None,
        vendedor_id=None,
    ) -> None:
        """Actualiza campos parciales de una devolución."""

    @abstractmethod
    def eliminar_devolucion(self, devolucion_id: str) -> None:
        """Elimina una devolución por ID lógico."""

    @abstractmethod
    def get_devoluciones(
        self,
        *,
        desde=None,
        hasta=None,
        vendedor_id: Optional[str] = None,
        estatus: Optional[str] = None,
    ) -> pd.DataFrame:
        """Lista devoluciones filtradas."""

    @abstractmethod
    def get_articulos(self, devolucion_id: str) -> pd.DataFrame:
        """Obtiene artículos de una devolución."""

    # ───────────────── PERSONAL ─────────────────
    @abstractmethod
    def crear_persona(self, nombre: str) -> str:
        """Crea persona y devuelve su ID."""

    @abstractmethod
    def listar_personal(self, *, solo_activos: bool = True) -> pd.DataFrame:
        """Lista personal."""

    @abstractmethod
    def actualizar_persona(self, persona_id: str, nuevo_nombre: str) -> None:
        """Actualiza nombre."""

    @abstractmethod
    def desactivar_persona(self, persona_id: str) -> None:
        """
        Desactiva persona (lógica o física).
        La implementación decide cómo.
        """

    # ───────────────── VENDEDORES ─────────────────
    @abstractmethod
    def crear_vendedor(self, persona_id: str, codigo: str, zona: str) -> str:
        """Crea vendedor."""

    @abstractmethod
    def listar_vendedores(self, *, solo_activos: bool = True) -> pd.DataFrame:
        """Lista vendedores."""

    @abstractmethod
    def desactivar_vendedor(self, vendedor_id: str) -> None:
        """Desactiva vendedor."""

    # ───────────────── ASIGNACIONES ─────────────────
    @abstractmethod
    def crear_asignacion(
        self,
        *,
        pasillo: str,
        persona_id: str,
        fecha_desde: str,
        fecha_hasta: str,
    ) -> str:
        """Crea asignación de pasillo."""

    @abstractmethod
    def listar_asignaciones(self) -> pd.DataFrame:
        """Lista asignaciones."""

    @abstractmethod
    def actualizar_asignacion(
        self,
        *,
        asignacion_id: str,
        pasillo: str,
        persona_id: str,
        fecha_desde: str,
        fecha_hasta: str,
    ) -> None:
        """Actualiza asignación."""

    @abstractmethod
    def eliminar_asignacion(self, asignacion_id: str) -> None:
        """Elimina asignación."""

    # ───────────────── PRODUCTOS ─────────────────
    @abstractmethod
    def listar_productos(self) -> pd.DataFrame:
        """Lista productos."""

    @abstractmethod
    def get_producto_por_clave(self, clave: str):
        """Obtiene producto por clave."""
        
    @abstractmethod
    def get_articulos(self, devolucion_id):
        raise NotImplementedError
