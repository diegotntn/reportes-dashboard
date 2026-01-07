from dotenv import load_dotenv
load_dotenv()

import webview

from ui.app.main_window import MainWindow
from ui.reportes.renderers.webview import WebViewRenderer


def main():
    # 1. Crear renderer
    web_renderer = WebViewRenderer(
        title="Dashboards de Reportes",
        width=1200,
        height=700
    )

    # 2. Crear ventana WebView (placeholder)
    web_renderer.create()

    # 3. Crear UI Tk (NO mainloop)
    app = MainWindow(web_renderer=web_renderer)

    # 4. Arrancar pywebview (HILO PRINCIPAL)
    def on_start():
        web_renderer.mark_ready()

    webview.start(on_start, debug=False)


if __name__ == "__main__":
    main()
