import webview


class WebViewRenderer:
    """
    Renderer global para dashboards HTML / Plotly usando pywebview.

    REGLAS:
    - webview.start() NO se llama aquí
    - webview.start() se llama UNA SOLA VEZ en main.py
    - Las vistas SOLO llaman set_html()
    - NO threads
    - NO callbacks Tkinter
    """

    def __init__(
        self,
        title: str = "Reportes",
        width: int = 1200,
        height: int = 700
    ):
        self.title = title
        self.width = width
        self.height = height

        self.window = None
        self._pending_html = None
        self._engine_ready = False

    # ─────────────────────────
    def create(self) -> None:
        """
        Crea la ventana WebView.

        Debe llamarse ANTES de webview.start().
        Es idempotente.
        """
        if self.window is not None:
            return

        self.window = webview.create_window(
            title=self.title,
            html=self._html_placeholder(),
            width=self.width,
            height=self.height,
            resizable=True
        )

    # ─────────────────────────
    def mark_ready(self) -> None:
        """
        Marca el engine como listo.
        Debe llamarse desde main.py DESPUÉS de webview.start().
        """
        self._engine_ready = True

        # Si había HTML pendiente, ahora sí renderizar
        if self._pending_html:
            self.window.load_html(self._pending_html)
            self._pending_html = None

    # ─────────────────────────
    def set_html(self, html: str) -> None:
        """
        Solicita el render de HTML.

        - Si el engine NO está listo → se guarda
        - Si el engine YA está listo → se renderiza
        """
        print("🌐 WebView.set_html() LLAMADO")
        print("🌐 HTML size:", len(html) if html else "None")

        if not self.window:
            print("⚠️ WebView aún no creada")
            return

        if not self._engine_ready:
            print("⏳ Engine no listo, HTML en espera")
            self._pending_html = html
            return

        self.window.load_html(html)

    # ─────────────────────────
    @staticmethod
    def _html_placeholder() -> str:
        """
        HTML base mostrado antes del primer render real.
        """
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1"/>
            <title>Cargando…</title>
            <style>
                body {
                    margin: 0;
                    padding: 24px;
                    font-family: Segoe UI, Roboto, Arial, sans-serif;
                    background: #0F172A;
                    color: #E5E7EB;
                }
                h3 {
                    margin-top: 0;
                    font-weight: 500;
                }
                p {
                    opacity: 0.85;
                }
            </style>
        </head>
        <body>
            <h3>Cargando reportes…</h3>
            <p>Espere un momento.</p>
        </body>
        </html>
        """
