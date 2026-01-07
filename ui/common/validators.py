from tkinter import messagebox


def required(value, message="Campo obligatorio"):
    if not value:
        raise ValueError(message)


def show_error(error: Exception, parent=None):
    messagebox.showerror(
        title="Error",
        message=str(error),
        parent=parent
    )


def safe_call(func, parent=None):
    """
    Ejecuta una función capturando errores
    y mostrándolos en UI.
    """
    try:
        func()
    except Exception as e:
        show_error(e, parent)
