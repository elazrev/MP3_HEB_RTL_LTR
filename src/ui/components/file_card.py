import flet as ft
from ...models.mp3_file import MP3File
from ...models.hebrew_handler import HebrewTextHandler
from ..styles import AppTheme


class FileCard(ft.UserControl):
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
                        on_change=self._handle_selection_change,
                        scale=1.2
                    ),

                    # Album Art
                    self._build_album_art(),

                    # File Details
                    ft.Column([
                        self._build_tag_preview("Title", 'title'),
                        self._build_tag_preview("Artist", 'artist'),
                        self._build_tag_preview("Album", 'album')
                    ], expand=True, spacing=5),

                    # Actions
                    ft.Column([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Convert Hebrew",
                            on_click=lambda e: self.on_convert(self.mp3_file) if self.on_convert else None,
                            icon_color=AppTheme.SECONDARY
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_color=AppTheme.ERROR,
                            tooltip="Remove from list",
                            on_click=lambda e: self.on_remove(self.mp3_file) if self.on_remove else None
                        )
                    ], spacing=0)
                ], alignment=ft.CrossAxisAlignment.START),
                padding=10
            ),
            elevation=1
        )

        return card

    def _build_album_art(self):
        """Build album art display"""
        if self.mp3_file.album_art:
            return ft.Container(
                content=ft.Image(
                    src=f"data:image/jpeg;base64,{self.mp3_file.album_art}",
                    width=50,
                    height=50,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(5),
                ),
                margin=ft.margin.only(right=10)
            )
        else:
            return ft.Container(
                content=ft.Icon(
                    ft.icons.ALBUM,
                    color=AppTheme.TEXT_SECONDARY,
                    size=24
                ),
                width=50,
                height=50,
                bgcolor=AppTheme.CARD_BACKGROUND,
                border_radius=5,
                border=ft.border.all(1, AppTheme.TEXT_HINT),
                alignment=ft.alignment.center,
                margin=ft.margin.only(right=10)
            )

    def _build_tag_preview(self, label: str, tag_name: str):
        """Build preview for a single tag"""
        original = self.mp3_file.original_tags[tag_name]
        new = self.mp3_file.tags[tag_name]

        # אם אין שינוי או אין טקסט עברי, הצג רק את הערך המקורי
        if original == new or not HebrewTextHandler.is_hebrew(original):
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=12, color=AppTheme.TEXT_SECONDARY),
                    ft.Text(original or "N/A", color=AppTheme.TEXT_PRIMARY)
                ], spacing=2),
                margin=ft.margin.only(bottom=5)
            )

        # אם יש שינוי, הצג את המקור והערך החדש
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, color=AppTheme.TEXT_SECONDARY),
                ft.Row([
                    ft.Text(
                        original,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH),
                        color=AppTheme.TEXT_SECONDARY,
                        size=14
                    ),
                    ft.Icon(
                        ft.icons.ARROW_FORWARD,
                        color=AppTheme.SECONDARY,
                        size=16
                    ),
                    ft.Text(
                        new,
                        color=AppTheme.PRIMARY,
                        weight=ft.FontWeight.BOLD,
                        size=14
                    )
                ], spacing=5)
            ], spacing=2),
            margin=ft.margin.only(bottom=5)
        )

    def _handle_selection_change(self, e):
        """Handle checkbox selection change"""
        self.mp3_file.selected = e.data == "true"  # Convert string to boolean
        if self.on_selection_change:
            self.on_selection_change(self.mp3_file)

    def update_selection(self, selected: bool):
        """Update the selection state externally"""
        self.mp3_file.selected = selected
        if hasattr(self, 'checkbox'):
            self.checkbox.value = selected
            self.update()