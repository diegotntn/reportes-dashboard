from tkinter import ttk
from typing import List, Any, Optional


class TkTableRenderer:
    """
    TkTableRenderer

    Renderer de TABLAS CLÁSICAS usando ttk.Treeview (Tkinter).

    Este renderer se utiliza para:
    - Vistas de detalle
    - Listados tabulares tradicionales
    - Información que NO requiere interactividad avanzada
      (zoom, hover complejo, animaciones)

    CASOS DE USO TÍPICOS:
    - Detalle de devoluciones
    - Listado de artículos
    - Tablas operativas (CRUD)

    PRINCIPIOS:
    - NO calcula datos.
    - NO transforma información.
    - NO conoce lógica de negocio.
    - SOLO recibe columnas y datos ya listos para mostrar.
    """

    def __init__(
        self,
        *,
        height: int = 12,
        show_scrollbar: bool = True
    ) -> None:
        """
        Inicializa el renderer de tablas Tkinter.

        Args:
            height (int):
                Número de filas visibles por defecto.

            show_scrollbar (bool):
                Indica si se debe mostrar scrollbar vertical.
        """
        self.height = height
        self.show_scrollbar = show_scrollbar

        self.tree: Optional[ttk.Treeview] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None

    # ─────────────────────────────────────────────
    def render(
        self,
        *,
        parent,
        columns: List[str],
        data: List[List[Any]],
        column_widths: Optional[List[int]] = None,
        headings: Optional[List[str]] = None
    ) -> None:
        """
        Renderiza la tabla Treeview dentro de un contenedor padre.

        Args:
            parent:
                Contenedor Tkinter donde se dibujará la tabla.

            columns (List[str]):
                Identificadores internos de columnas.

            data (List[List[Any]]):
                Datos de la tabla, una lista por fila.

            column_widths (Optional[List[int]]):
                Anchos personalizados de columnas.

            headings (Optional[List[str]]):
                Títulos visibles de columnas.
                Si es None, se usan los nombres de `columns`.
        """

        self.clear()

        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=self.height
        )

        # Configurar encabezados
        for idx, col in enumerate(columns):
            title = headings[idx] if headings else col
            width = column_widths[idx] if column_widths else 120

            self.tree.heading(col, text=title)
            self.tree.column(col, width=width, anchor="w")

        # Insertar filas
        for row in data:
            self.tree.insert("", "end", values=row)

        self.tree.pack(fill="both", expand=True, side="left")

        # Scrollbar opcional
        if self.show_scrollbar:
            self.scrollbar = ttk.Scrollbar(
                parent,
                orient="vertical",
                command=self.tree.yview
            )
            self.tree.configure(yscrollcommand=self.scrollbar.set)
            self.scrollbar.pack(fill="y", side="right")

    # ─────────────────────────────────────────────
    def update(self, data: List[List[Any]]) -> None:
        """
        Actualiza los datos de la tabla sin recrear columnas.

        Args:
            data (List[List[Any]]):
                Nuevos datos de la tabla.
        """
        if not self.tree:
            return

        self.clear_rows()

        for row in data:
            self.tree.insert("", "end", values=row)

    # ─────────────────────────────────────────────
    def clear_rows(self) -> None:
        """
        Elimina todas las filas de la tabla.
        """
        if not self.tree:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

    # ─────────────────────────────────────────────
    def clear(self) -> None:
        """
        Elimina completamente la tabla y su scrollbar.
        """
        if self.tree:
            self.tree.destroy()
            self.tree = None

        if self.scrollbar:
            self.scrollbar.destroy()
            self.scrollbar = None

    # ─────────────────────────────────────────────
    def destroy(self) -> None:
        """
        Destruye explícitamente los recursos del renderer.
        """
        self.clear()
