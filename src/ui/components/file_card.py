import flet as ft
from ...models.mp3_file import MP3File
from ..styles import AppTheme

class FileCard(ft.UserControl):
    def __init__(
        self, 
        mp3_file: MP3File, 
        on_convert=None, 
        on_remove=None, 
        on_selection_change=None
    ):
        super().__init__()
        self.mp3_file = mp3_file
        self.on_convert = on_convert
        self.on_remove = on_remove
        self.on_selection_change = on_selection_change

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    # Selection checkbox
                    ft.Checkbox(
                        value=self.mp3_file.selected,
                        on_change=lambda e: self._handle_selection_change(e.control.value),
                        tooltip="Select this file"
                    ),
                    
                    # Album art (if exists)
                    self._build_album_art(),
                    
                    # File details with changes indicator
                    ft.Column([
                        self._build_tag_row("Title", 'title'),
                        self._build_tag_row("Artist", 'artist'),
                        self._build_tag_row("Album", 'album')
                    ], expand=True),
                    
                    # Action buttons
                    ft.Column([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            tooltip="Convert Hebrew text",
                            on_click=lambda e: self.on_convert(self.mp3_file) if self.on_convert else None,
                            icon_color=AppTheme.PRIMARY
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            tooltip="Remove from list",
                            on_click=lambda e: self.on_remove(self.mp3_file) if self.on_remove else None,
                            icon_color=AppTheme.ERROR
                        )
                    ])
                ]),
                bgcolor=AppTheme.CARD_BACKGROUND if not self.mp3_file.has_changes() 
                else ft.colors.with_opacity(0.1, AppTheme.PRIMARY),
                padding=10,
                border_radius=8
            ),
            elevation=2
        )

    def _build_album_art(self):
        """Build album art display"""
        if self.mp3_file.album_art:
            return ft.Image(
                src=f"data:image/jpeg;base64,{self.mp3_file.album_art}",
                width=50,
                height=50,
                fit=ft.ImageFit.COVER,
                border_radius=8
            )
        return ft.Container(
            content=ft.Icon(ft.icons.ALBUM, color=AppTheme.TEXT_SECONDARY),
            width=50,
            height=50,
            bgcolor=AppTheme.BACKGROUND,
            border_radius=8
        )

    def _build_tag_row(self, label: str, tag_name: str):
        """Build a row for tag display with change indication"""
        original = self.mp3_file.original_tags[tag_name]
        current = self.mp3_file.tags[tag_name]
        has_changed = original != current

        if not has_changed:
            return ft.Text(f"{label}: {current}")

        return ft.Column([
            ft.Text(label, size=12, color=AppTheme.TEXT_SECONDARY),
            ft.Row([
                ft.Text(
                    original,
                    style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH),
                    color=AppTheme.TEXT_SECONDARY,
                    size=12
                ),
                ft.Icon(
                    ft.icons.ARROW_FORWARD,
                    color=AppTheme.SECONDARY,
                    size=16
                ),
                ft.Text(
                    current,
                    color=AppTheme.PRIMARY,
                    weight=ft.FontWeight.BOLD
                )
            ])
        ])

    def _handle_selection_change(self, value: bool):
        """Handle checkbox selection change"""
        self.mp3_file.selected = value
        if self.on_selection_change:
            self.on_selection_change(self.mp3_file)