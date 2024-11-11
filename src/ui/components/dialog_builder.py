import flet as ft
from ..styles import AppTheme, AppAnimations

class DialogBuilder:
    @staticmethod
    def create_confirmation_dialog(
        page: ft.Page,
        title: str,
        content: str,
        on_confirm,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        danger: bool = False
    ) -> ft.AlertDialog:
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.icons.WARNING_AMBER_ROUNDED if danger else ft.icons.INFO_OUTLINE,
                        color=AppTheme.ERROR if danger else AppTheme.PRIMARY,
                        size=40
                    ),
                    ft.Container(height=AppTheme.PADDING_MEDIUM),
                    ft.Text(
                        content,
                        text_align=ft.TextAlign.CENTER,
                        size=16
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20
            ),
            actions=[
                ft.TextButton(
                    cancel_text,
                    style=ft.ButtonStyle(
                        color={"": AppTheme.TEXT_SECONDARY}
                    ),
                    on_click=lambda e: DialogBuilder.close_dialog(page)
                ),
                ft.ElevatedButton(
                    confirm_text,
                    style=AppTheme.get_button_style(danger=danger),
                    on_click=lambda e: DialogBuilder._handle_confirm(page, on_confirm)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: None
        )

    @staticmethod
    def show_error_dialog(
        page: ft.Page,
        title: str,
        content: str,
        on_close=None
    ):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.icons.ERROR_OUTLINE,
                        color=AppTheme.ERROR,
                        size=40
                    ),
                    ft.Container(height=AppTheme.PADDING_MEDIUM),
                    ft.Text(
                        content,
                        text_align=ft.TextAlign.CENTER,
                        size=16
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=20
            ),
            actions=[
                ft.ElevatedButton(
                    "Close",
                    style=AppTheme.get_button_style(),
                    on_click=lambda e: DialogBuilder._handle_confirm(page, on_close)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    @staticmethod
    def close_dialog(page: ft.Page):
        """Close the current dialog"""
        if page.dialog:
            page.dialog.open = False
            page.update()

    @staticmethod
    def _handle_confirm(page: ft.Page, callback):
        """Handle confirmation and close dialog"""
        DialogBuilder.close_dialog(page)
        if callback:
            callback()