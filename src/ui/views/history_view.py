import flet as ft
from typing import Optional, Callable
from ...models.hebrew_fixer import HebrewFixer
from ..components.history_item import HistoryItemCard
from ..styles import AppStyles, AppTheme
from ..widgets.custom_button import CustomButton


class HistoryView(ft.UserControl):
    def __init__(self, fixer: HebrewFixer, on_undo: Optional[Callable] = None):
        super().__init__()
        self.fixer = fixer
        self.on_undo = on_undo
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all UI components"""
        self.history_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=500,
            auto_scroll=True
        )
        self.clear_button = CustomButton(
            text="Clear History",
            icon=ft.icons.DELETE_FOREVER,
            primary=False,
            danger=True,
            on_click=self._handle_clear_history
        )

    def build(self):
        return ft.Column([
            # Header with clear button
            ft.Row([
                ft.Text(
                    "Change History",
                    style=AppStyles.SUBHEADER
                ),
                self.clear_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            # History list
            self.history_list if len(self.fixer.history) > 0 else self._build_empty_state()

        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_empty_state(self):
        """Build empty state display"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.icons.HISTORY,
                    size=48,
                    color=AppTheme.TEXT_SECONDARY
                ),
                ft.Text(
                    "No changes made yet",
                    size=16,
                    color=AppTheme.TEXT_SECONDARY,
                    italic=True
                )
            ], alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True
        )

    def update_history(self):
        """Update the history view"""
        try:
            self.history_list.controls.clear()
            history_items = reversed(self.fixer.history)  # Show newest first

            for item in history_items:
                self.history_list.controls.append(
                    HistoryItemCard(
                        history_item=item,
                        on_undo=self.on_undo
                    )
                )

            self.clear_button.set_disabled(len(self.fixer.history) == 0)
            self.update()

        except Exception as e:
            print(f"Error updating history: {str(e)}")

    def _handle_clear_history(self, _):
        """Handle clear history button click"""

        def confirm_clear(e):
            if e.data == "yes":
                self.fixer.history.clear()
                self.update_history()
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Clear History?"),
            content=ft.Text("This will permanently remove all history entries. This action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False)),
                ft.TextButton(
                    "Clear",
                    on_click=confirm_clear,
                    style=ft.ButtonStyle(color=AppTheme.ERROR)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if self.page:
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()