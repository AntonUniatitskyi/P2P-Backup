import flet as ft
from app.ui.gui import main_gui

if __name__ == "__main__":
    # Запускаем приложение как десктопную программу
    ft.app(target=main_gui)

# Если захочешь запустить это в браузере (например, как веб-панель на сервере),
# просто поменяй на: ft.app(target=main_gui, view=ft.AppView.WEB_BROWSER)