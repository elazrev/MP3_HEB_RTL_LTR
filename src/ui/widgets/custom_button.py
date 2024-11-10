import flet as ft
from ..styles import AppTheme


class CustomButton(ft.UserControl):
    def __init__(
        self,
        text: str,
        on_click=None,
        icon=None,
        primary: bool = True,
        disabled: bool = False,
        danger: bool = False
    ):
        super().__init__()
        self.text = text
        self.on_click = on_click
        self.icon = icon
        self.primary = primary
        self.disabled = disabled
        self.danger = danger

    def build(self):
        return ft.ElevatedButton(
            text=self.text,
            icon=self.icon,
            on_click=self.on_click,
            disabled=self.disabled,
            style=self._get_button_style()
        )

    def _get_button_style(self):
        if self.danger:
            color = AppTheme.ERROR
        elif self.primary:
            color = AppTheme.PRIMARY
        else:
            color = AppTheme.SECONDARY

        return ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: AppTheme.TEXT_PRIMARY,
                ft.ControlState.DISABLED: AppTheme.TEXT_SECONDARY,
            },
            bgcolor={
                ft.ControlState.DEFAULT: color,
                ft.ControlState.DISABLED: AppTheme.BACKGROUND,
            },
            padding=10,
            shape=ft.RoundedRectangleBorder(radius=8),
            elevation={"pressed": 0, "default": 2},
            animation_duration=100,
        )

    def set_disabled(self, disabled: bool):
        """Update button disabled state"""
        self.disabled = disabled
        if self.page:
            self.update()