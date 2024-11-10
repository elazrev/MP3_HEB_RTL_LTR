from typing import Callable

import flet as ft

from ..styles import AppTheme


class ActionButtons(ft.UserControl):
    def __init__(
            self,
            on_select_files: Callable,
            on_select_directory: Callable,
            on_clear: Callable
    ):
        super().__init__()
        self.on_select_files = on_select_files
        self.on_select_directory = on_select_directory
        self.on_clear = on_clear

    def build(self):
        return ft.Row([
            ft.ElevatedButton(
                text="Select MP3 Files",
                icon=ft.icons.FOLDER_OPEN,
                on_click=self.on_select_files,
                style=self._get_button_style()
            ),
            ft.Container(width=10),
            ft.ElevatedButton(
                text="Select Directory",
                icon=ft.icons.FOLDER,
                on_click=self.on_select_directory,
                style=self._get_button_style()
            ),
            ft.Container(width=10),
            ft.ElevatedButton(
                text="Clear Screen",
                icon=ft.icons.CLEAR_ALL,
                on_click=self.on_clear,
                style=self._get_button_style(False)
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

    @staticmethod
    def _get_button_style(primary: bool = True):
        return ft.ButtonStyle(
            color={
                ft.MaterialState.DEFAULT: AppTheme.TEXT_PRIMARY,
                ft.MaterialState.DISABLED: AppTheme.TEXT_SECONDARY,
            },
            bgcolor={
                ft.MaterialState.DEFAULT: AppTheme.PRIMARY if primary else AppTheme.SECONDARY,
                ft.MaterialState.DISABLED: AppTheme.BACKGROUND,
            },
            padding=10,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation={"pressed": 0, "default": 2},
        )
