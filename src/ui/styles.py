import flet as ft
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AppTheme:
    """Application theme configuration"""
    # Main colors
    PRIMARY: str = "#4A90E2"
    SECONDARY: str = "#2ECC71"
    BACKGROUND: str = "#2C3E50"
    ERROR: str = "#E74C3C"
    WARNING: str = "#F1C40F"

    # Text colors
    TEXT_PRIMARY: str = "#FFFFFF"
    TEXT_SECONDARY: str = "#B3B3B3"

    # Card styles
    CARD_BACKGROUND: str = "#34495E"
    CARD_BORDER_RADIUS: int = 10

    @classmethod
    def get_theme(cls) -> Dict[str, Any]:
        """Get Flet theme configuration"""
        return {
            "color_scheme_seed": cls.PRIMARY,
            "use_material3": True,
            "visual_density": ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        }


@dataclass
class AppStyles:
    """Application-wide styles"""

    # Text styles
    HEADER = ft.TextStyle(
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.GREY_300,
        foreground=ft.Paint(
            color=ft.colors.BLUE_700,
            stroke_width=2,
            stroke_join=ft.StrokeJoin.ROUND,
            style=ft.PaintingStyle.STROKE,
        ),

    )

    SUBHEADER = ft.TextStyle(
        size=20,
        weight=ft.FontWeight.BOLD,
        color=AppTheme.SECONDARY
    )

    BODY = ft.TextStyle(
        size=16,
        color=AppTheme.TEXT_PRIMARY
    )

    # Button styles
    @staticmethod
    def get_button_style(primary: bool = True) -> ft.ButtonStyle:
        return ft.ButtonStyle(
            color={
                ft. ControlState.DEFAULT: AppTheme.TEXT_PRIMARY,
                ft. ControlState.DISABLED: AppTheme.TEXT_SECONDARY,
            },
            bgcolor={
                ft. ControlState.DEFAULT: AppTheme.PRIMARY if primary else AppTheme.SECONDARY,
                ft. ControlState.DISABLED: AppTheme.BACKGROUND,
            },
            padding=50,
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation={"pressed": 0, "default": 2},
        )

    # Container styles
    CARD_STYLE = {
        "bgcolor": AppTheme.CARD_BACKGROUND,
        "border_radius": AppTheme.CARD_BORDER_RADIUS,
        "padding": 20,
    }

    # Layout
    CONTENT_PADDING = 20
    SPACING = 10

    @staticmethod
    def get_elevated_button_props(primary: bool = True) -> Dict[str, Any]:
        """Get consistent elevated button properties"""
        return {
            "style": AppStyles.get_button_style(primary),
            "elevation": 2,
        }