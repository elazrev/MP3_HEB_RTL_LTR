import flet as ft
from src.ui.views.main_view import MainView
from src.ui.styles import AppTheme


def main(page: ft.Page):
    """Initialize and run the application"""

    # Configure page
    page.title = "Hebrew MP3 Tag Fixer"
    page.window.width = 1200
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    # Apply theme
    page.theme = AppTheme.get_theme()

    # Create main view
    main_view = MainView()

    # Add main view to page
    page.add(main_view)

    # Initialize pickers after adding to page
    main_view.initialize_pickers()

    # Update page
    page.update()


if __name__ == '__main__':
    ft.app(
        target=main,
        assets_dir="assets",
    )