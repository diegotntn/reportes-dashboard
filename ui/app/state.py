class AppState:
    """
    Estado compartido de la aplicación.

    RESPONSABILIDADES:
    - Coordinar actualizaciones entre módulos
    - Exponer callbacks comunes
    """

    def __init__(self):
        self._on_data_change_callbacks = []

    # ─────────────────────────────
    def subscribe_data_change(self, callback):
        """
        Registra un callback que se ejecuta
        cuando cambian datos del sistema.
        """
        if callable(callback):
            self._on_data_change_callbacks.append(callback)

    def notify_data_change(self):
        """
        Notifica a todos los observadores
        que hubo cambios en los datos.
        """
        for cb in self._on_data_change_callbacks:
            cb()
