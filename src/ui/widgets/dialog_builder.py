import flet as ft
from ..styles import AppTheme


class DialogBuilder:
    @staticmethod
    def create_confirmation_dialog(
            page: ft.Page,
            title: str,
            content: str,
            on_confirm: callable,
            confirm_text: str = "Confirm",
            cancel_text: str = "Cancel",
            danger: bool = False
    ):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(content),
            actions=[
                ft.TextButton(
                    cancel_text,
                    on_click=lambda e: setattr(dialog, 'open', False)
                ),
                ft.TextButton(
                    confirm_text,
                    on_click=lambda e: (on_confirm(e), setattr(dialog, 'open', False)),
                    style=ft.ButtonStyle(
                        color=AppTheme.ERROR if danger else AppTheme.PRIMARY
                    )
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.dialog = dialog
        dialog.open = True
        page.update()