from .base_control import BaseControl
import flet as ft
from ...models.mp3_file import MP3File
from ..styles import AppTheme


class FileCard(BaseControl):
    def __init__(self, mp3_file: MP3File, on_convert=None, on_remove=None, on_selection_change=None):
        super().__init__()
        self.mp3_file = mp3_file
        self.on_convert = on_convert
        self.on_remove = on_remove
        self.on_selection_change = on_selection_change

    def build(self):
        card = ft.Card(
            content=ft.Container(
                content=ft.Row([
                    # Checkbox
                    ft.Checkbox(
                        value=self.mp3_file.selected,
                        on_change=self._handle_selection_change
                    ),

                    # Album Art
                    self._build_album_art(),

                    # File Details
                    ft.Column([
                        self._build_tag_preview("Title", 'title'),
                        self._build_tag_preview("Artist", 'artist'),
                        self._build_tag_preview("Album", 'album')
                    ], expand=True),

                    # Actions
                    ft.Column([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Convert Hebrew",
                            on_click=lambda e: self.on_convert(self.mp3_file) if self.on_convert else None
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color=AppTheme.ERROR,
                            tooltip="Remove from list",
                            on_click=lambda e: self.on_remove(self.mp3_file) if self.on_remove else None
                        )
                    ])
                ]),
                padding=10
            )
        )

        return card

    def _build_album_art(self):
        """Build album art display"""
        if self.mp3_file.album_art:
            return ft.Image(
                src=f"data:image/jpeg;base64,{self.mp3_file.album_art}",
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
                border_radius=ft.border_radius.all(5),
            )
        else:
            return ft.Container(
                content=ft.Icon(
                    ft.icons.ALBUM,
                    color=AppTheme.TEXT_SECONDARY
                ),
                width=50,
                height=50,
                bgcolor=AppTheme.CARD_BACKGROUND,
                border_radius=5,
                border=ft.border.all(1, AppTheme.TEXT_HINT)
            )

    def _build_tag_preview(self, label: str, tag_name: str):
        """Build preview for a single tag"""
        original = self.mp3_file.original_tags[tag_name]
        new = self.mp3_file.tags[tag_name]

        if original == new:
            return ft.Text(f"{label}: {original}")

        return ft.Column([
            ft.Text(label, size=12, color=AppTheme.TEXT_SECONDARY),
            ft.Row([
                ft.Text(
                    original,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH),
                    color=AppTheme.TEXT_SECONDARY
                ),
                ft.Text(" → "),
                ft.Text(
                    new,
                    color=AppTheme.PRIMARY,
                    weight=ft.FontWeight.BOLD
                )
            ])
        ])

    def _handle_selection_change(self, e):
        """Handle checkbox selection change"""
        self.mp3_file.selected = e.value
        if self.on_selection_change:
            self.on_selection_change(self.mp3_file)