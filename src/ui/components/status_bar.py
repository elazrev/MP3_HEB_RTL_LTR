import flet as ft
from ..styles import AppStyles, AppTheme

class StatusBar(ft.UserControl):
    def __init__(self):
        super().__init__()
        self._initialize_components()

    def _initialize_components(self):
        self.status_text = ft.Text(
            color=AppTheme.SECONDARY,
            size=16,
            weight=ft.FontWeight.W_500
        )
        self.progress_bar = ft.ProgressBar(
            visible=False,
            color=AppTheme.SECONDARY,
            bgcolor=AppTheme.BACKGROUND
        )

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([self.status_text],
                      alignment=ft.MainAxisAlignment.CENTER),
                self.progress_bar,
            ]),
            padding=10
        )

    def show_error(self, message: str):
        """Show error message"""
        self.status_text.value = f"Error: {message}"
        self.status_text.color = AppTheme.ERROR
        self.progress_bar.visible = False
        self.update()

    def show_success(self, message: str):
        """Show success message"""
        self.status_text.value = message
        self.status_text.color = AppTheme.SECONDARY
        self.progress_bar.visible = False
        self.update()

    def show_progress(self, message: str):
        """Show progress message"""
        self.status_text.value = message
        self.status_text.color = AppTheme.SECONDARY
        self.progress_bar.visible = True
        self.update()