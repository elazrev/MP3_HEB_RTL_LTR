import flet as ft
from ...models.mp3_file import MP3File
from ..styles import AppTheme, AppAnimations


class FileCard(ft.UserControl):
    def __init__(self, mp3_file: MP3File, on_convert=None, on_remove=None):
        super().__init__()
        self.mp3_file = mp3_file
        self.on_convert = on_convert
        self.on_remove = on_remove
        self.animation = AppAnimations.get_fade_in()

    def build(self):
        return ft.Container(
            content=self._build_card_content(),
            **AppTheme.get_card_style(),
            animate=self.animation
        )

    def _build_card_content(self):
        if self.mp3_file.has_hebrew():
            return self._build_hebrew_content()
        return self._build_simple_content()

    def _build_hebrew_content(self):
        title_preview = self.mp3_file.get_tag_preview('title')
        artist_preview = self.mp3_file.get_tag_preview('artist')
        album_preview = self.mp3_file.get_tag_preview('album')

        return ft.Column([
            # File Header
            ft.Row([
                ft.Icon(ft.icons.MUSIC_NOTE, color=AppTheme.PRIMARY),
                ft.Container(width=AppTheme.PADDING_SMALL),
                ft.Text("Hebrew Text Detected",
                        color=AppTheme.PRIMARY,
                        weight=ft.FontWeight.BOLD)
            ]),

            ft.Divider(height=1, color=AppTheme.TEXT_HINT),

            # Title Section
            self._build_preview_section(
                "Title",
                title_preview['original'],
                title_preview['converted'],
                is_hebrew=True
            ),

            # Artist Section
            self._build_preview_section(
                "Artist",
                artist_preview['original'],
                artist_preview['converted'],
                is_hebrew=artist_preview['analysis']['contains_hebrew']
            ),

            # Album Section
            self._build_preview_section(
                "Album",
                album_preview['original'],
                album_preview['converted'],
                is_hebrew=album_preview['analysis']['contains_hebrew']
            ),

            # Actions
            ft.Row([
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.EDIT,
                        icon_color=AppTheme.SECONDARY,
                        tooltip="Convert Hebrew",
                        on_click=lambda e: self.on_convert(self.mp3_file) if self.on_convert else None
                    ),
                    tooltip="Convert Hebrew text to LTR"
                ),
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=AppTheme.ERROR,
                        tooltip="Remove file",
                        on_click=lambda e: self.on_remove(self.mp3_file) if self.on_remove else None
                    ),
                    tooltip="Remove file from list"
                )
            ], alignment=ft.MainAxisAlignment.END)
        ])

    def _build_preview_section(self, label: str, original: str, converted: str, is_hebrew: bool):
        if not is_hebrew:
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=12, color=AppTheme.TEXT_HINT),
                    ft.Text(original)
                ]),
                padding=ft.padding.symmetric(vertical=AppTheme.PADDING_SMALL)
            )

        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, color=AppTheme.TEXT_HINT),
                ft.Row([
                    ft.Container(
                        content=ft.Text(
                            original,
                            color=AppTheme.TEXT_SECONDARY,
                            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                        ),
                        tooltip="Original text"
                    ),
                    ft.Icon(
                        ft.icons.ARROW_FORWARD,
                        color=AppTheme.SECONDARY,
                        size=16
                    ),
                    ft.Container(
                        content=ft.Text(
                            converted,
                            color=AppTheme.SECONDARY,
                            weight=ft.FontWeight.BOLD
                        ),
                        tooltip="Converted text"
                    )
                ])
            ]),
            padding=ft.padding.symmetric(vertical=AppTheme.PADDING_SMALL)
        )

    def _build_simple_content(self):
        return ft.Column([
            ft.Row([
                ft.Icon(ft.icons.MUSIC_NOTE, color=AppTheme.TEXT_HINT),
                ft.Container(width=AppTheme.PADDING_SMALL),
                ft.Text(self.mp3_file.tags['title'] or self.mp3_file.get_display_path())
            ]),
            ft.Container(height=AppTheme.PADDING_SMALL),
            ft.Text(
                f"Artist: {self.mp3_file.tags['artist']}" if self.mp3_file.tags['artist'] else "No artist",
                color=AppTheme.TEXT_SECONDARY,
                size=14
            ),
            ft.Text(
                f"Album: {self.mp3_file.tags['album']}" if self.mp3_file.tags['album'] else "No album",
                color=AppTheme.TEXT_SECONDARY,
                size=14
            ),
            ft.Row([
                ft.Container(
                    content=ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color=AppTheme.ERROR,
                        tooltip="Remove file",
                        on_click=lambda e: self.on_remove(self.mp3_file) if self.on_remove else None
                    ),
                    tooltip="Remove file from list"
                )
            ], alignment=ft.MainAxisAlignment.END)
        ])
