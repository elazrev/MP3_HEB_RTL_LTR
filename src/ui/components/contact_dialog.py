import flet as ft
import webbrowser
from ..styles import AppTheme


class ContactManager:
    """Manages contact dialog and button creation"""

    def __init__(self, page: ft.Page):
        self.page = page

    def create_contact_button(self) -> ft.Container:
        """Create a styled contact button"""
        return ft.Container(
            content=ft.TextButton(
                text="elaz.rev",
                tooltip="Click to contact",
                on_click=self.show_contact_dialog,
                style=ft.ButtonStyle(
                    color={"": "#666666"},
                    bgcolor={"": "transparent"},
                    overlay_color={"": "transparent"},
                    padding=0,

                ),
            )
        )

    def show_contact_dialog(self, _):
        """Show contact information dialog"""
        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Contact Information"),
            content=ft.Column([
                ft.Text("Would you like to get in touch?"),
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.icons.EMAIL, color=AppTheme.PRIMARY),
                    ft.TextButton(
                        "elaz.rev@gmail.com",
                        on_click=lambda _: self._open_email(),
                        style=ft.ButtonStyle(color={"": AppTheme.PRIMARY})
                    )
                ]),
                ft.Container(height=5),
                ft.Text(
                    "Click the email address to open your mail client",
                    size=12,
                    color="#666666",
                    italic=True
                )
            ]),
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _open_email(self):
        """Open default mail client with pre-filled email"""
        webbrowser.open('mailto:elaz.rev@gmail.com?subject=Hebrew%20MP3%20Tag%20Fixer%20Contact')

    def _close_dialog(self, dialog):
        """Close dialog and remove from overlay"""
        dialog.open = False
        try:
            self.page.overlay.remove(dialog)
        except ValueError:
            pass
        self.page.update()