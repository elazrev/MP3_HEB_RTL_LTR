import flet as ft
from ...models.mp3_file import MP3File
from ..styles import AppStyles, AppTheme


class FilePreviewCard(ft.UserControl):
    def __init__(self, mp3_file: MP3File, on_remove=None):
        super().__init__()
        self.mp3_file = mp3_file
        self.on_remove = on_remove

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=self._build_card_content(),
                padding=20,
                bgcolor=AppTheme.CARD_BACKGROUND
            )
        )

    def _build_card_content(self):
        return ft.Column([
            # Header with remove button
            ft.Row([
                ft.Text(
                    "File Preview",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.PRIMARY
                ),
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_color=AppTheme.ERROR,
                    tooltip="Remove from list",
                    on_click=self._handle_remove
                ) if self.on_remove else None
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Divider(color=AppTheme.SECONDARY, height=1),

            # Main content
            ft.Row([
                # Album art or placeholder
                self._build_album_art(),

                # File details
                ft.Column([
                    self._build_tag_comparison("Title",
                                               self.mp3_file.original_tags['title'],
                                               self.mp3_file.tags['title']
                                               ),
                    self._build_tag_comparison("Artist",
                                               self.mp3_file.original_tags['artist'],
                                               self.mp3_file.tags['artist']
                                               ),
                    self._build_tag_comparison("Album",
                                               self.mp3_file.original_tags['album'],
                                               self.mp3_file.tags['album']
                                               ),
                    self._build_tag_comparison("Filename",
                                               self.mp3_file.original_tags['filename'],
                                               self.mp3_file.tags['filename']
                                               ),
                ], spacing=10, expand=True)
            ])
        ])

    def _build_album_art(self):
        """Build album art display"""
        if self.mp3_file.album_art:
            return ft.Container(
                content=ft.Image(
                    src=f"data:image/jpeg;base64,{self.mp3_file.album_art}",
                    width=100,
                    height=100,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=ft.border_radius.all(10),
                ),
                margin=ft.margin.only(right=20)
            )
        else:
            return ft.Container(
                width=100,
                height=100,
                bgcolor=AppTheme.BACKGROUND,
                border_radius=10,
                content=ft.Icon(
                    ft.icons.ALBUM,
                    color=AppTheme.PRIMARY,
                    size=40
                ),
                margin=ft.margin.only(right=20)
            )

    def _build_tag_comparison(self, label: str, original: str, new: str):
        """Build a row showing original and new values for a tag"""
        has_changed = original != new
        return ft.Container(
            content=ft.Column([
                ft.Text(label, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(
                        original,
                        color=AppTheme.TEXT_SECONDARY,
                        size=14,
                        style=ft.TextDecoration.LINE_THROUGH if has_changed else None,
                    ),
                    ft.Icon(
                        ft.icons.ARROW_FORWARD,
                        color=AppTheme.SECONDARY,
                        size=16
                    ) if has_changed else None,
                    ft.Text(
                        new,
                        color=AppTheme.SECONDARY,
                        size=14,
                        weight=ft.FontWeight.BOLD if has_changed else None,
                    ) if has_changed else None,
                ])
            ]),
            bgcolor=AppTheme.BACKGROUND if has_changed else None,
            padding=10 if has_changed else None,
            border_radius=5 if has_changed else None,
        )

    def _handle_remove(self, _):
        """Handle remove button click"""
        if self.on_remove:
            self.on_remove(self.mp3_file)