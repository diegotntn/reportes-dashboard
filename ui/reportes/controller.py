class ReportesController:
    """
    Controlador de reportes (SINCRONO).

    RESPONSABILIDADES:
    - Ejecutar la generación de reportes
    - NO usar threads
    - NO usar root.after
    - NO tocar directamente la UI
    - Entregar el resultado al callback de render

    NOTA:
    Este controlador está diseñado para trabajar con:
    - pywebview como loop principal
    - Render síncrono de dashboards
    """

    def __init__(self, service, on_result):
        """
        service: ReportesService
        on_result: callback UI para renderizar resultados
        """
        self.service = service
        self.on_result = on_result

    # ─────────────────────────────
    def actualizar(self, filtros: dict) -> None:
        """
        Ejecuta la generación de reportes de forma síncrona.
        """
        resultado = self.service.generar(**filtros)
        self.on_result(resultado)
