# app/ui/ready_files_gui.py
import flet as ft
import shutil
import os


def show_ready_files_window(ready_files, ready_dir):
    def main(page: ft.Page):
        page.title = "Восстановленные файлы"
        page.window_width = 500
        page.window_height = 400

        save_picker = ft.FilePicker()
        page.overlay.append(save_picker)

        list_view = ft.ListView(expand=True, spacing=8)

        for basename, path in ready_files:
            def make_save_handler(src_path):
                def save_as(e):
                    def on_result(res: ft.FilePickerResultEvent):
                        if res.path:
                            shutil.copy(src_path, res.path)
                    save_picker.on_result = on_result
                    save_picker.save_file(file_name=os.path.basename(src_path))
                return save_as

            list_view.controls.append(
                ft.Row([
                    ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                    ft.Text(basename, expand=True),
                    ft.ElevatedButton("Сохранить как...", on_click=make_save_handler(path))
                ])
            )

        page.add(ft.Text("Файлы, собранные из подключённых флешек:", weight="bold"), list_view)

    ft.app(target=main)