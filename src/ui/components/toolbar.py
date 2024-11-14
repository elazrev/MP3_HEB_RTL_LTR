import flet as ft
from ..styles import AppTheme


class Toolbar(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.save_selected_btn = None

    def build(self):
        self.save_selected_btn = ft.ElevatedButton(
            "Save Selected Files",
            icon=ft.icons.SAVE,
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: AppTheme.TEXT_PRIMARY},
                bgcolor={ft.ControlState.DEFAULT: AppTheme.PRIMARY},
                padding=10,
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            disabled=True  # Initially disabled
        )

        return ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    "Select Files",
                    icon=ft.icons.FOLDER_OPEN,
                    style=ft.ButtonStyle(
                        color={ft.ControlState.DEFAULT: AppTheme.TEXT_PRIMARY},
                        bgcolor={ft.ControlState.DEFAULT: AppTheme.SECONDARY}
                    )
                ),
                self.save_selected_btn,
                ft.ElevatedButton(
                    "Clear Selection",
                    icon=ft.icons.CLEAR_ALL,
                    style=ft.ButtonStyle(
                        color={ft.ControlState.DEFAULT: AppTheme.TEXT_PRIMARY},
                        bgcolor={ft.ControlState.DEFAULT: AppTheme.ERROR}
                    )
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10
        )

    def update_save_button(self, has_selected: bool):
        """Update save button state based on selection"""
        if self.save_selected_btn:
            self.save_selected_btn.disabled = not has_selected
            self.update()