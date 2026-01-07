class ReportesState:
    """
    Estado actual del módulo de reportes.
    """

    def __init__(self):
        self.filtros = None
        self.resultado = None

    def set(self, filtros, resultado):
        self.filtros = filtros
        self.resultado = resultado
