import flet as ft
from ..styles import AppTheme
from typing import Callable

class Toolbar(ft.UserControl):
    def __init__(self,
                 on_select_files=None,
                 on_select_directory=None,
                 on_clear=None,
                 on_save_selected=None,
                 on_convert_selected=None):  # הוספת callback חדש
        super().__init__()
        self.on_select_files = on_select_files
        self.on_select_directory = on_select_directory
        self.on_clear = on_clear
        self.on_save_selected = on_save_selected
        self.on_convert_selected = on_convert_selected
        self.convert_btn = None
        self.save_btn = None

    def build(self):
        self.convert_btn = ft.ElevatedButton(
            text="Convert Selected",
            icon=ft.icons.TRANSLATE,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: AppTheme.TEXT_PRIMARY},
                bgcolor={ft.MaterialState.DEFAULT: AppTheme.SECONDARY}
            ),
            on_click=self.on_convert_selected,
            disabled=True
        )

        self.save_btn = ft.ElevatedButton(
            text="Save Selected",
            icon=ft.icons.SAVE,
            style=ft.ButtonStyle(
                color={ft.MaterialState.DEFAULT: AppTheme.TEXT_PRIMARY},
                bgcolor={ft.MaterialState.DEFAULT: AppTheme.PRIMARY}
            ),
            on_click=self.on_save_selected,
            disabled=True
        )

        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    text="Select Files",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=self.on_select_files
                ),
                ft.ElevatedButton(
                    text="Select Directory",
                    icon=ft.icons.FOLDER,
                    on_click=self.on_select_directory
                ),
                self.convert_btn,
                self.save_btn,
                ft.ElevatedButton(
                    text="Clear",
                    icon=ft.icons.CLEAR_ALL,
                    on_click=self.on_clear
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10
        )

    def update_buttons_state(self, has_selected: bool, has_changes: bool):
        """Update buttons state based on selection and changes"""
        if self.convert_btn:
            self.convert_btn.disabled = not has_selected
        if self.save_btn:
            self.save_btn.disabled = not (has_selected and has_changes)
        self.update()

