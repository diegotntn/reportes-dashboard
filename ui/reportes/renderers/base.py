from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseRenderer(ABC):
    """
    Contrato visual base para TODOS los renderers del sistema.

    Este contrato define la interfaz mínima que cualquier renderer
    (Plotly, Tkinter, Canvas, HTML, etc.) debe implementar para poder
    integrarse de forma consistente con las vistas del sistema.

    PRINCIPIOS:
    - El renderer SOLO dibuja (visualización).
    - El renderer NO calcula datos.
    - El renderer NO accede a Mongo ni a servicios.
    - El renderer NO conoce filtros ni estado de la aplicación.
    - El renderer recibe datos ya procesados y listos para mostrar.

    OBJETIVO:
    - Garantizar intercambiabilidad de renderers.
    - Permitir dashboards vivos y actualizables.
    - Mantener una arquitectura limpia y desacoplada.
    """

    def __init__(self, parent: Optional[Any] = None) -> None:
        """
        Inicializa el renderer.

        Args:
            parent (Optional[Any]):
                Contenedor visual donde se renderizará el contenido.
                Puede ser un Frame de Tkinter, un contenedor HTML,
                o cualquier objeto requerido por la implementación concreta.
        """
        self.parent = parent

    @abstractmethod
    def render(self, data: Any) -> None:
        """
        Renderiza por primera vez el contenido visual.

        Este método se ejecuta cuando:
        - El renderer se crea por primera vez.
        - Se muestran datos iniciales.
        - Se monta una vista completa.

        Debe crear la estructura visual necesaria (figura, widgets,
        componentes HTML, etc.) y mostrarla en el contenedor asignado.

        Args:
            data (Any):
                Datos ya procesados y listos para mostrar.
                Ejemplos: dict, list, pandas.DataFrame.
        """
        raise NotImplementedError("render() debe ser implementado por el renderer")

    @abstractmethod
    def update(self, data: Any) -> None:
        """
        Actualiza el contenido visual existente sin recrearlo completamente.

        Este método se utiliza para:
        - Refrescos automáticos.
        - Sensación de tiempo real.
        - Animaciones suaves.
        - Cambios de datos sin parpadeo.

        La implementación debe procurar:
        - Mantener el estado visual cuando sea posible.
        - Evitar destrucción innecesaria de componentes.
        - Aplicar transiciones suaves si la tecnología lo permite.

        Args:
            data (Any):
                Nuevos datos ya procesados y listos para mostrar.
        """
        raise NotImplementedError("update() debe ser implementado por el renderer")

    @abstractmethod
    def clear(self) -> None:
        """
        Limpia el contenido visual del renderer.

        Se utiliza cuando:
        - Se cambia de vista.
        - No hay datos para mostrar.
        - Se necesita reiniciar el componente visual.

        Debe eliminar o resetear el contenido gráfico sin afectar
        al contenedor padre.
        """
        raise NotImplementedError("clear() debe ser implementado por el renderer")

    def destroy(self) -> None:
        """
        Destruye de forma explícita los recursos visuales del renderer.

        Este método es opcional y puede ser sobrescrito por
        implementaciones concretas cuando se requiera liberar:
        - Widgets
        - Figuras
        - Recursos gráficos
        - Memoria asociada

        Por defecto, delega en clear().
        """
        self.clear()
