import flet as ft


class AppTheme:
    # Colors - גווני כחול-אפור בהירים יותר
    PRIMARY = "#6C8EBF"  # כחול רך יותר
    SECONDARY = "#82B366"  # ירוק רך
    BACKGROUND = "#F5F5F5"  # רקע בהיר מאוד
    CARD_BACKGROUND = "#FFFFFF"  # רקע לבן לכרטיסיות
    ERROR = "#D85959"  # אדום רך יותר
    SUCCESS = "#76B376"  # ירוק רך
    WARNING = "#E8B460"  # כתום רך

    # Text Colors
    TEXT_PRIMARY = "#2E2E2E"  # כמעט שחור
    TEXT_SECONDARY = "#666666"  # אפור כהה
    TEXT_HINT = "#999999"  # אפור בהיר

    # Spacing
    PADDING_SMALL = 8
    PADDING_MEDIUM = 12
    PADDING_LARGE = 16

    # Border Radius
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_LARGE = 12

    # Window Size
    WINDOW_WIDTH = 800  # רוחב חלון קטן יותר
    WINDOW_HEIGHT = 600  # גובה חלון קטן יותר

    @staticmethod
    def get_card_style():
        return {
            "bgcolor": AppTheme.CARD_BACKGROUND,
            "border_radius": AppTheme.BORDER_RADIUS_MEDIUM,
            "padding": AppTheme.PADDING_MEDIUM,
            "border": ft.border.all(1, "#E0E0E0")  # מסגרת עדינה
        }

    @staticmethod
    def get_button_style(primary: bool = True, danger: bool = False):
        color = AppTheme.ERROR if danger else (AppTheme.PRIMARY if primary else AppTheme.SECONDARY)
        return ft.ButtonStyle(
            color={"": AppTheme.TEXT_PRIMARY},
            bgcolor={"": color, "hovered": ft.colors.with_opacity(0.8, color)},
            animation_duration=200,
            side=ft.BorderSide(width=0),
            shape=ft.RoundedRectangleBorder(radius=AppTheme.BORDER_RADIUS_MEDIUM)
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