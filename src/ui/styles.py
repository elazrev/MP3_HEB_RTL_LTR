import flet as ft


class AppInfo:
    """Application information and constants"""
    VERSION = "0.1.0-beta"
    AUTHOR = "elaz.rev"
    TITLE = "Hebrew MP3 Tag Fixer"
    DESCRIPTION = "Fix Hebrew text in MP3 tags from RTL to LTR"


class AppTheme:
    # Colors - גווני כחול מודרניים
    PRIMARY = "#3498db"  # כחול בהיר
    SECONDARY = "#2ecc71"  # ירוק נעים
    BACKGROUND = "#f8f9fa"  # אפור בהיר מאוד
    CARD_BACKGROUND = "#ffffff"  # לבן
    ERROR = "#e74c3c"  # אדום
    SUCCESS = "#27ae60"  # ירוק כהה
    WARNING = "#f1c40f"  # צהוב

    # Text Colors
    TEXT_PRIMARY = "#2c3e50"  # כחול כהה
    TEXT_SECONDARY = "#7f8c8d"  # אפור
    TEXT_HINT = "#95a5a6"  # אפור בהיר

    # Gradients
    HEADER_GRADIENT = ["#3498db", "#2980b9"]

    # Shadows
    CARD_SHADOW = ft.BoxShadow(
        spread_radius=1,
        blur_radius=8,
        color=ft.colors.with_opacity(0.1, "black"),
        offset=ft.Offset(0, 2)
    )

    # Window Size
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600

    @staticmethod
    def get_card_style(hoverable: bool = False):
        return {
            "bgcolor": AppTheme.CARD_BACKGROUND,
            "border_radius": 8,
            "padding": 16,
            "shadow": AppTheme.CARD_SHADOW,
            "animate": 300 if hoverable else None,
        }

    @staticmethod
    def get_button_style(primary: bool = True, danger: bool = False):
        color = (
            AppTheme.ERROR if danger
            else AppTheme.PRIMARY if primary
            else AppTheme.SECONDARY
        )
        return ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor={
                ft.ControlState.DEFAULT: color,
                ft.ControlState.HOVERED: ft.colors.with_opacity(0.9, color),
            },
            elevation={"pressed": 0, "default": 2},
            animation_duration=200,
            padding=14,
            shape=ft.RoundedRectangleBorder(radius=8),
        )

class AppAnimations:
    DURATION_SHORT = 200
    DURATION_MEDIUM = 300
    DURATION_LONG = 400

    @staticmethod
    def get_fade_in():
        return ft.animation.Animation(
            duration=AppAnimations.DURATION_MEDIUM,
            curve=ft.AnimationCurve.EASE_OUT
        )

    @staticmethod
    def get_slide_in():
        return ft.animation.Animation(
            duration=AppAnimations.DURATION_MEDIUM,
            curve=ft.AnimationCurve.EASE_OUT_BACK
        )