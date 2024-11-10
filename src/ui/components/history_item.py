import flet as ft
import os
import platform
import subprocess
from typing import Dict
from ..styles import AppStyles, AppTheme


class HistoryItemCard(ft.UserControl):
    """Component for displaying a history item"""

    def __init__(self, history_item: Dict):
        super().__init__()
        self.item = history_item

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=self._build_card_content(),
                padding=20,
                bgcolor=AppTheme.CARD_BACKGROUND
            )
        )

    def _build_card_content(self):
        """Build the main card content"""
        return ft.Column([
            # Header with timestamp and actions
            self._build_header(),

            ft.Divider(color=AppTheme.SECONDARY, height=1),

            # File details
            self._build_file_details(),

            # Changes summary
            self._build_changes_summary()
        ])

    def _build_header(self):
        """Build the card header with timestamp and actions"""
        return ft.Row([
            ft.Column([
                ft.Text(
                    "Modified:",
                    size=12,
                    color=AppTheme.TEXT_SECONDARY
                ),
                ft.Text(
                    self.item['date'],
                    size=14,
                    color=AppTheme.PRIMARY,
                    weight=ft.FontWeight.BOLD
                )
            ]),
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    icon_color=AppTheme.SECONDARY,
                    tooltip="Open containing folder",
                    on_click=self._open_file_location
                ),
                ft.IconButton(
                    icon=ft.icons.INFO_OUTLINE,
                    icon_color=AppTheme.PRIMARY,
                    tooltip="Show details",
                    on_click=self._show_details
                )
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _build_file_details(self):
        """Build the file details section"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "File Details",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.SECONDARY
                ),
                self._build_path_display(),
            ]),
            padding=10,
            border_radius=5,
            bgcolor=AppTheme.BACKGROUND
        )

    def _build_path_display(self):
        """Build the file path display with copy button"""
        return ft.Row([
            ft.Text(
                os.path.basename(self.item['path']),
                size=14,
                color=AppTheme.TEXT_PRIMARY,
                overflow=ft.TextOverflow.ELLIPSIS,
                expand=True
            ),
            ft.IconButton(
                icon=ft.icons.COPY,
                icon_color=AppTheme.SECONDARY,
                tooltip="Copy path",
                on_click=lambda _: self.page.set_clipboard(self.item['path'])
            )
        ])

    def _build_changes_summary(self):
        """Build the summary of changes made"""
        changes = []
        for tag in ['title', 'artist', 'album', 'filename']:
            if self.item['original_tags'][tag] != self.item['new_tags'][tag]:
                changes.append(self._build_change_row(
                    tag.capitalize(),
                    self.item['original_tags'][tag],
                    self.item['new_tags'][tag]
                ))

        return ft.Column([
            ft.Text(
                "Changes Made",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=AppTheme.SECONDARY
            ),
            *changes
        ]) if changes else None

    def _build_change_row(self, label: str, original: str, new: str):
        """Build a row showing a single change"""
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, color=AppTheme.TEXT_SECONDARY),
                ft.Row([
                    ft.Text(
                        original,
                        size=14,
                        color=AppTheme.TEXT_SECONDARY,
                        text_decoration=ft.TextDecoration.LINE_THROUGH
                    ),
                    ft.Icon(
                        ft.icons.ARROW_FORWARD,
                        color=AppTheme.SECONDARY,
                        size=16
                    ),
                    ft.Text(
                        new,
                        size=14,
                        color=AppTheme.PRIMARY,
                        weight=ft.FontWeight.BOLD
                    )
                ])
            ]),
            padding=10,
            bgcolor=AppTheme.BACKGROUND,
            border_radius=5
        )

    def _open_file_location(self, _):
        """Open the containing folder in system file explorer"""
        try:
            path = os.path.dirname(self.item['path'])
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error opening folder: {str(e)}"),
                        bgcolor=AppTheme.ERROR
                    )
                )

    def _show_details(self, _):
        """Show detailed information in a dialog"""
        try:
            dialog = ft.AlertDialog(
                title=ft.Text("Change Details"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Full Path:", weight=ft.FontWeight.BOLD),
                        ft.SelectableText(self.item['path']),
                        ft.Divider(),
                        ft.Text("Original Tags:", weight=ft.FontWeight.BOLD),
                        self._build_tags_display(self.item['original_tags']),
                        ft.Divider(),
                        ft.Text("New Tags:", weight=ft.FontWeight.BOLD),
                        self._build_tags_display(self.item['new_tags'])
                    ]),
                    padding=20,
                    bgcolor=AppTheme.CARD_BACKGROUND
                ),
                actions=[
                    ft.TextButton(
                        "Close",
                        on_click=lambda e: setattr(dialog, 'open', False)
                    )
                ]
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        except Exception as e:
            if self.page:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error showing details: {str(e)}"),
                        bgcolor=AppTheme.ERROR
                    )
                )

    def _build_tags_display(self, tags: Dict):
        """Build a display for tag information"""
        return ft.Column([
            ft.Row([
                ft.Text(f"{key}:", weight=ft.FontWeight.BOLD),
                ft.Text(value)
            ]) for key, value in tags.items() if key != 'modified_date'
        ])