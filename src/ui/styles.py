from dataclasses import dataclass
from typing import Dict, Any
import flet as ft


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
            "visual_density": ft.ThemeVisualDensity.COMFORTABLE,
        }


@dataclass
class AppStyles:
    """Application-wide styles"""

    # Text styles
    HEADER = ft.TextStyle(
        size=30,
        weight=ft.FontWeight.BOLD,
        color=AppTheme.PRIMARY
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
    PRIMARY_BUTTON = {
        "bgcolor": AppTheme.PRIMARY,
        "color": AppTheme.TEXT_PRIMARY,
        "height": 40,
        "style": ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    }

    SECONDARY_BUTTON = {
        "bgcolor": AppTheme.SECONDARY,
        "color": AppTheme.TEXT_PRIMARY,
        "height": 40,
        "style": ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    }

    # Container styles
    CARD_STYLE = {
        "bgcolor": AppTheme.CARD_BACKGROUND,
        "border_radius": AppTheme.CARD_BORDER_RADIUS,
        "padding": 15,
    }

    # Layout styles
    CONTENT_PADDING = 20
    SPACING = 10

    @staticmethod
    def get_elevated_button_style(primary: bool = True) -> Dict[str, Any]:
        """Get consistent button style"""
        style = AppStyles.PRIMARY_BUTTON if primary else AppStyles.SECONDARY_BUTTON
        return {
            **style,
            "elevation": 2,
        }