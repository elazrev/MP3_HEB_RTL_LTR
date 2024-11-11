import flet as ft


class AppTheme:
    # Colors
    PRIMARY = "#4A90E2"  # כחול עיקרי
    SECONDARY = "#2ECC71"  # ירוק משני
    BACKGROUND = "#1E1E1E"  # רקע כהה
    CARD_BACKGROUND = "#2D2D2D"  # רקע כרטיסיה
    ERROR = "#E74C3C"  # אדום לשגיאות
    SUCCESS = "#27AE60"  # ירוק להצלחות
    WARNING = "#F39C12"  # כתום לאזהרות

    # Text Colors
    TEXT_PRIMARY = "#FFFFFF"  # טקסט ראשי
    TEXT_SECONDARY = "#B3B3B3"  # טקסט משני
    TEXT_HINT = "#757575"  # טקסט רמז

    # Spacing
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24

    # Border Radius
    BORDER_RADIUS_SMALL = 4
    BORDER_RADIUS_MEDIUM = 8
    BORDER_RADIUS_LARGE = 12

    @staticmethod
    def get_card_style():
        return {
            "bgcolor": AppTheme.CARD_BACKGROUND,
            "border_radius": AppTheme.BORDER_RADIUS_MEDIUM,
            "padding": AppTheme.PADDING_MEDIUM,
            "shadow": ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.with_opacity(0.3, "black"),
                offset=ft.Offset(0, 2)
            )
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