from .base_control import BaseControl
import flet as ft
from ..styles import AppTheme, AppAnimations


class Toolbar(BaseControl):
    def __init__(self, on_select_files=None, on_select_directory=None, on_clear=None, on_save=None):
        super().__init__()
        self.on_select_files = on_select_files
        self.on_select_directory = on_select_directory
        self.on_clear = on_clear
        self.on_save = on_save
        self.save_button = None

    def build(self):
        self.save_button = ft.ElevatedButton(
            "Save Changes",
            icon=ft.icons.SAVE,
            style=AppTheme.get_button_style(),
            on_click=self.on_save,
            disabled=True
        )

        return ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        "Select MP3 Files",
                        icon=ft.icons.FOLDER_OPEN,
                        style=AppTheme.get_button_style(),
                        on_click=self.on_select_files
                    ),
                    ft.Container(width=AppTheme.PADDING_SMALL),
                    ft.ElevatedButton(
                        "Select Directory",
                        icon=ft.icons.FOLDER,
                        style=AppTheme.get_button_style(),
                        on_click=self.on_select_directory
                    ),
                    ft.Container(width=AppTheme.PADDING_SMALL),
                    ft.ElevatedButton(
                        "Clear All",
                        icon=ft.icons.CLEAR_ALL,
                        style=AppTheme.get_button_style(primary=False),
                        on_click=self.on_clear
                    ),
                    ft.Container(width=AppTheme.PADDING_SMALL),
                    self.save_button
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            animate=AppAnimations.get_fade_in(),
            padding=ft.padding.symmetric(
                vertical=AppTheme.PADDING_MEDIUM
            )
        )

    def update_save_button(self, has_changes: bool):
        """Update save button state"""
        if self.save_button:
            self.save_button.disabled = not has_changes
            self.update()