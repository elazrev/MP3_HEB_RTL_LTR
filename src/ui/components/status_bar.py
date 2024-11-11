import flet as ft
from ..styles import AppTheme, AppAnimations


class StatusBar(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.status_text = None
        self.progress_ring = None
        self.init_components()

    def init_components(self):
        self.status_text = ft.Text(
            color=AppTheme.TEXT_SECONDARY,
            size=14,
            weight=ft.FontWeight.W_500
        )

        self.progress_ring = ft.ProgressRing(
            width=16,
            height=16,
            stroke_width=2,
            color=AppTheme.SECONDARY,
            visible=False
        )

    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    self.progress_ring,
                    ft.Container(width=8),
                    self.status_text
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

    def show_progress(self, message: str):
        """Show progress message with spinner"""
        self.status_text.value = message
        self.status_text.color = AppTheme.TEXT_SECONDARY
        self.progress_ring.visible = True
        self.update()

    def show_success(self, message: str):
        """Show success message with icon"""
        self.status_text.value = message
        self.status_text.color = AppTheme.SUCCESS
        self.progress_ring.visible = False
        self.update()

    def show_error(self, message: str):
        """Show error message with icon"""
        self.status_text.value = f"Error: {message}"
        self.status_text.color = AppTheme.ERROR
        self.progress_ring.visible = False
        self.update()

    def clear(self):
        """Clear status message"""
        self.status_text.value = None
        self.progress_ring.visible = False
        self.update()