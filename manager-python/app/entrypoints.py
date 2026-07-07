def run_gui():
    import flet as ft
    from app.ui.gui import main_gui
    ft.app(target=main_gui)


def run_daemon():
    from app.daemon_main import run_daemon as _run
    _run()