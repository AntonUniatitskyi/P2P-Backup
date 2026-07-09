import flet as ft
import os
from app.config import Config
from app.services.go_bridge import GoBridge
from app.services.discovery_service import DiscoveryService


def main_gui(page: ft.Page):
    page.title = Config.APP_TITLE
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = Config.WINDOW_WIDTH
    page.window_height = Config.WINDOW_HEIGHT
    page.padding = 20

    bridge = GoBridge(Config.GO_BINARY_PATH)

    # Единый словарь состояния приложения
    state = {
        "selected_file_paths": [],
        "split_directories": [],
        "restore_directories": []
    }

    # --- Элементы отображения логов ---
    log_console = ft.ListView(expand=True, spacing=5, auto_scroll=True, height=120)

    def log(message: str, color="white"):
        log_console.controls.append(ft.Text(message, color=color, font_family="Consolas"))
        page.update()

    # ================= В К Л А Д К А  1 :  Б Э К А П =================
    dirs_list_view_split = ft.ListView(expand=False, height=120, spacing=5)
    files_list_view_split = ft.ListView(expand=False, height=100, spacing=5)
    req_split_text = ft.Text("Выбрано папок: 0 из 5", weight="bold", color=ft.Colors.ORANGE_300)
    file_name_text = ft.Text("Файлы не выбраны", italic=True)

    def update_split_ui():
        dirs_list_view_split.controls.clear()
        k, m = int(data_slider.value), int(parity_slider.value)
        total = k + m
        req_split_text.value = f"Выбрано папок: {len(state['split_directories'])} из {total} (K:{k} + M:{m})"

        for idx, path in enumerate(state["split_directories"]):
            def remove_dir(e, index=idx):
                state["split_directories"].pop(index)
                update_split_ui()

            dirs_list_view_split.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.DRIVE_FILE_RENAME_OUTLINE, color=ft.Colors.BLUE_200),
                    ft.Text(path, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=remove_dir)
                ])
            )

        dirs_ok = len(state["split_directories"]) == total
        files_ok = len(state["selected_file_paths"]) > 0
        split_btn.disabled = not (dirs_ok and files_ok)
        page.update()

    def update_files_ui():
        files_list_view_split.controls.clear()
        for idx, path in enumerate(state["selected_file_paths"]):
            def remove_file(e, index=idx):
                state["selected_file_paths"].pop(index)
                update_files_ui()

            files_list_view_split.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE, color=ft.Colors.GREEN_200),
                    ft.Text(os.path.basename(path), expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=remove_file)
                ])
            )
        file_name_text.value = f"Выбрано файлов: {len(state['selected_file_paths'])}"
        update_split_ui()
        page.update()

    def start_backup(e):
        files = state["selected_file_paths"]
        if not files:
            log("[Ошибка] Выберите хотя бы один файл!", "red")
            return

        # Проверка на коллизии имён — иначе шарды на флешках перезатрутся
        names = [os.path.basename(f) for f in files]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            log(f"[Ошибка] Обнаружены файлы с одинаковым именем: {', '.join(duplicates)}. "
                f"Переименуйте один из них перед бэкапом.", "red")
            return

        log(f"\n[Процесс] Запуск бэкапа {len(files)} файл(ов)...", "cyan")
        success_count = 0
        for file_path in files:
            log(f"[Файл] {os.path.basename(file_path)}...", "white")
            try:
                output = bridge.run_split(file_path, int(data_slider.value), int(parity_slider.value),
                                          state["split_directories"])
                log(output, "green")
                success_count += 1
            except Exception as ex:
                log(f"[Ошибка ядра] {os.path.basename(file_path)}: {str(ex)}", "red")

        log(f"\n[Итог] Успешно обработано: {success_count} из {len(files)}", "cyan")

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                if f.path not in state["selected_file_paths"]:
                    state["selected_file_paths"].append(f.path)
            log(f"[Система] Добавлено файлов: {len(e.files)}")
        update_files_ui()

    def on_split_dir_picked(e: ft.FilePickerResultEvent):
        if e.path and e.path not in state["split_directories"]:
            state["split_directories"].append(e.path)
            update_split_ui()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    dir_picker_split = ft.FilePicker(on_result=on_split_dir_picked)

    pick_file_btn = ft.ElevatedButton("1. Выбрать файл(ы)", icon=ft.Icons.FOLDER_OPEN,
                                      on_click=lambda _: file_picker.pick_files(allow_multiple=True))

    data_slider = ft.Slider(min=1, max=8, divisions=7, value=3, label="{value} блоков данных",
                            on_change=lambda _: update_split_ui())
    parity_slider = ft.Slider(min=1, max=4, divisions=3, value=2, label="{value} блоков резерва",
                              on_change=lambda _: update_split_ui())

    add_dir_split_btn = ft.ElevatedButton("2. Добавить папку флешки", icon=ft.Icons.ADD_TO_DRIVE,
                                          on_click=lambda _: dir_picker_split.get_directory_path())
    split_btn = ft.FilledButton("3. Начать распределенный бэкап", icon=ft.Icons.PLAY_ARROW, on_click=start_backup,
                                disabled=True)

    tab_split = ft.Column([
        ft.Row([pick_file_btn, file_name_text]),
        ft.Container(content=files_list_view_split, border=ft.border.all(1, ft.Colors.WHITE10), border_radius=8,
                     padding=10),
        ft.Divider(),
        ft.Text("Основные блоки данных (K)"), data_slider,
        ft.Text("Резервные блоки четности (M)"), parity_slider,
        ft.Divider(),
        ft.Row([add_dir_split_btn, req_split_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(content=dirs_list_view_split, border=ft.border.all(1, ft.Colors.WHITE10), border_radius=8,
                     padding=10),
        ft.Container(content=split_btn, alignment=ft.alignment.center, margin=ft.margin.only(top=10))
    ], scroll=ft.ScrollMode.AUTO)

    # ================= В К Л А Д К А  2 :  В О С С Т А Н О В Л Е Н И Е =================
    # K и M больше не запрашиваются у пользователя — Go-ядро само читает их
    # из манифеста (.meta), который был сохранён рядом с шардами при бэкапе.
    dirs_list_view_restore = ft.ListView(expand=False, height=120, spacing=5)
    req_restore_text = ft.Text("Укажите папки для поиска чанков", weight="bold", color=ft.Colors.BLUE_200)

    found_files_dropdown = ft.Dropdown(
        label="Обнаруженные файлы на дисках",
        width=450,
        hint_text="Сначала добавьте папки поиска..."
    )

    def update_restore_ui():
        dirs_list_view_restore.controls.clear()
        req_restore_text.value = f"Добавлено путей для сканирования: {len(state['restore_directories'])}"

        found_names = DiscoveryService.find_restorable_files(state["restore_directories"])
        found_files_dropdown.options = [ft.dropdown.Option(name) for name in found_names]

        if not found_names:
            found_files_dropdown.hint_text = "Файлы не обнаружены. Проверьте папки."
            if found_files_dropdown.value not in found_names:
                found_files_dropdown.value = None
        else:
            found_files_dropdown.hint_text = f"Найдено файлов: {len(found_names)}"

        for idx, path in enumerate(state["restore_directories"]):
            def remove_dir_res(e, index=idx):
                state["restore_directories"].pop(index)
                update_restore_ui()

            dirs_list_view_restore.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER, color=ft.Colors.ORANGE_200),
                    ft.Text(path, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=remove_dir_res)
                ])
            )
        restore_btn.disabled = len(state["restore_directories"]) == 0
        page.update()

    def start_restore(e):
        filename = found_files_dropdown.value
        if not filename:
            log("[Ошибка] Выберите обнаруженный файл из списка!", "red")
            return

        target_path = os.path.abspath(f"./restored_{filename}")
        log(f"\n[Процесс] Начинаем сборку файла в {target_path}...", "cyan")

        try:
            output = bridge.run_join(filename, target_path, state["restore_directories"])
            log(output, "green")
        except Exception as ex:
            log(f"[Ошибка восстановления]: {str(ex)}", "red")

    def on_restore_dir_picked(e: ft.FilePickerResultEvent):
        if e.path and e.path not in state["restore_directories"]:
            state["restore_directories"].append(e.path)
            update_restore_ui()

    dir_picker_restore = ft.FilePicker(on_result=on_restore_dir_picked)

    add_dir_restore_btn = ft.ElevatedButton("Указать папку поиска", icon=ft.Icons.FOLDER_SHARED,
                                            on_click=lambda _: dir_picker_restore.get_directory_path())
    restore_btn = ft.FilledButton("Собрать файл из кусков", icon=ft.Icons.BUILD, on_click=start_restore, disabled=True)

    page.overlay.extend([file_picker, dir_picker_split, dir_picker_restore])

    tab_restore = ft.Column([
        ft.Text("1. Выберите файл из обнаруженных на флешках:"),
        found_files_dropdown,
        ft.Divider(),
        ft.Text("2. Укажите папки, где могут находиться куски файла:"),
        ft.Row([add_dir_restore_btn, req_restore_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(content=dirs_list_view_restore, border=ft.border.all(1, ft.Colors.WHITE10), border_radius=8,
                     padding=10),
        ft.Container(content=restore_btn, alignment=ft.alignment.center, margin=ft.margin.only(top=10))
    ], scroll=ft.ScrollMode.AUTO)

    # ================= Г Л А В Н Ы Й  Э К Р А Н =================
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Создать бэкап (Split)", content=ft.Container(content=tab_split, padding=10)),
            ft.Tab(text="Восстановить файл (Join)", content=ft.Container(content=tab_restore, padding=10)),
        ],
        expand=True
    )

    page.add(
        ft.Text(Config.APP_TITLE, size=22, weight="bold", color=ft.Colors.BLUE_400),
        tabs,
        ft.Text("Консоль операций:"),
        ft.Container(content=log_console, bgcolor=ft.Colors.BLACK87, padding=10, border_radius=8)
    )

    update_split_ui()
    update_files_ui()
    update_restore_ui()