import flet as ft
from typing import Optional
from ...models.hebrew_fixer import HebrewFixer
from .editor_view import EditorView
from ..styles import AppStyles, AppTheme


class MainView(ft.UserControl):
    def __init__(self):
        super().__init__()
        self.fixer = HebrewFixer()
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all UI components"""
        self.editor_view = EditorView(self.fixer)

    def build(self):
        """Build the main view"""
        return ft.Column([
            # Header
            ft.Row([
                ft.Text(
                    "TRAKTOR Hebrew MP3 Tag Fixer",
                    style=AppStyles.HEADER
                )
            ], alignment=ft.MainAxisAlignment.CENTER),

            # Credit
            ft.Row([
                ft.Text(
                    "© by elaz.rev",
                    size=14,
                    italic=True,
                    color=AppTheme.SECONDARY
                )
            ], alignment=ft.MainAxisAlignment.CENTER),

            # Main content
            self.editor_view,

        ], expand=True)

    def initialize_pickers(self):
        """Initialize file pickers after the view is mounted"""
        self.editor_view.initialize_pickers()