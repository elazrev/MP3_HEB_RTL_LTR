import flet as ft
from flet import Page
from src.models.mp3_file import MP3File
from src.ui.components.file_card import FileCard
from src.ui.components.status_bar import StatusBar
from src.ui.components.dialog_builder import DialogBuilder
from src.ui.styles import AppTheme, AppInfo
import os


class HebrewMP3App:
    def __init__(self, page: Page):
        self.page = page
        self.files_to_process = {}
        self.setup_page()
        self.initialize_components()
        self.build_ui()

    def setup_page(self):
        """Configure the page settings"""
        self.page.title = AppInfo.TITLE
        self.page.window.width = AppTheme.WINDOW_MIN_WIDTH
        self.page.window.height = AppTheme.WINDOW_MIN_HEIGHT
        self.page.window.min_width = AppTheme.WINDOW_MIN_WIDTH
        self.page.window.min_height = AppTheme.WINDOW_MIN_HEIGHT
        self.page.padding = 0  # Remove padding for full-width header
        self.page.bgcolor = AppTheme.BACKGROUND
        self.page.window.center()  # Center the window on screen

        # Set theme mode
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            visual_density=ft.VisualDensity.COMFORTABLE  # Fixed deprecation warning
        )

    def initialize_components(self):
        """Initialize UI components"""
        # File pickers
        self.file_picker = ft.FilePicker(on_result=self.on_files_picked)
        self.dir_picker = ft.FilePicker(on_result=self.on_directory_picked)
        self.page.overlay.extend([self.file_picker, self.dir_picker])

        # Status bar
        self.status_bar = StatusBar()

        # Action buttons container
        self.action_buttons = ft.Container(
            content=ft.Row([
                ft.ElevatedButton(
                    text="Select Files",
                    icon=ft.icons.FOLDER_OPEN,
                    on_click=lambda _: self.file_picker.pick_files(
                        allow_multiple=True,
                        allowed_extensions=['mp3']
                    ),
                    style=AppTheme.get_button_style()
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Select Directory",
                    icon=ft.icons.FOLDER,
                    on_click=lambda _: self.dir_picker.get_directory_path(),
                    style=AppTheme.get_button_style()
                ),
                ft.Container(width=10),
                ft.ElevatedButton(
                    text="Clear All",
                    icon=ft.icons.CLEAR_ALL,
                    on_click=self.clear_files,
                    style=AppTheme.get_button_style(primary=False)
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=20
        )

        # Files list
        self.files_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=10,
            height=400,
            auto_scroll=True
        )

        # Selection controls
        self.select_all_checkbox = ft.Checkbox(
            value=False,
            on_change=self._handle_select_all
        )

        # Bulk action buttons
        self.bulk_actions = ft.Row([
            ft.ElevatedButton(
                text="Convert Selected",
                icon=ft.icons.EDIT,
                on_click=self._handle_convert_selected,
                style=AppTheme.get_button_style(),
                disabled=True
            ),
            ft.Container(width=10),
            ft.ElevatedButton(
                text="Save Changes",
                icon=ft.icons.SAVE,
                on_click=self._handle_save_selected,
                style=AppTheme.get_button_style(primary=True),
                disabled=True
            )
        ], visible=False)

        # Progress bar
        self.progress_bar = ft.ProgressBar(
            visible=False,
            color=AppTheme.SECONDARY,
            bgcolor=ft.colors.with_opacity(0.1, AppTheme.SECONDARY)
        )

    def build_ui(self):
        """Build the main UI"""
        # Header with gradient
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    AppInfo.TITLE,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE
                ),
                ft.Text(
                    f"by {AppInfo.AUTHOR}",
                    size=14,
                    italic=True,
                    color=ft.colors.WHITE70
                )
            ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=AppTheme.HEADER_GRADIENT
            ),
            padding=20,
            border_radius=ft.border_radius.only(bottom_left=16, bottom_right=16),
            shadow=AppTheme.CARD_SHADOW
        )

        # Files section with improved visuals
        files_section = ft.Container(
            content=ft.Column([
                # Section header
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            ft.Icon(ft.icons.FOLDER_OPEN, color=AppTheme.PRIMARY),
                            ft.Text(
                                "Files with Hebrew",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AppTheme.TEXT_PRIMARY
                            )
                        ]),
                        ft.Container(
                            content=ft.Text(
                                f"{len(self.files_to_process)} files",
                                color=AppTheme.TEXT_SECONDARY,
                                size=14
                            ),
                            bgcolor=AppTheme.BACKGROUND,
                            padding=ft.padding.all(8),
                            border_radius=16
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(bottom=12)
                ),

                # Selection controls
                ft.Container(
                    content=ft.Row([
                        ft.Row([
                            self.select_all_checkbox,
                            ft.Text(
                                "Select All Files",
                                color=AppTheme.TEXT_PRIMARY,
                                weight=ft.FontWeight.BOLD,
                                size=14
                            )
                        ]),
                        self.bulk_actions
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    bgcolor=AppTheme.BACKGROUND,
                    border_radius=8,
                    visible=bool(self.files_to_process)
                ),

                # Status and progress
                ft.Container(
                    content=ft.Column([
                        self.status_bar,
                        self.progress_bar
                    ]),
                    padding=ft.padding.symmetric(vertical=8)
                ),

                # Files list
                ft.Container(
                    content=self.files_list,
                    padding=8,
                    bgcolor=AppTheme.BACKGROUND,
                    border_radius=8,
                    expand=True
                )
            ]),
            padding=20
        )

        # Version footer
        footer = ft.Container(
            content=ft.Row([
                ft.Text(
                    f"Version {AppInfo.VERSION}",
                    size=12,
                    color=AppTheme.TEXT_HINT
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=10
        )

        # Add all components to page
        self.page.add(
            header,
            self.action_buttons,
            files_section,
            footer
        )

    def _update_ui(self):
        """Update UI safely"""
        if self.page:
            self.page.update()

    def on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        # Clear existing files when selecting new files
        self.files_to_process.clear()
        self.status_bar.show_progress(f"Processing files...")

        # Process files with detailed error handling and logging
        total_files = len(e.files)
        processed_files = 0
        hebrew_files = 0

        for f in e.files:
            try:
                processed_files += 1
                self.status_bar.show_progress(f"Processing file {processed_files}/{total_files}")

                mp3_file = MP3File(f.path)
                if mp3_file.has_hebrew():
                    self.files_to_process[f.path] = mp3_file
                    hebrew_files += 1

            except Exception as error:
                print(f"Error processing {f.name}: {str(error)}")  # Debug logging

        # Update UI with results
        if hebrew_files > 0:
            self.status_bar.show_success(
                f"Found {hebrew_files} files with Hebrew text out of {total_files} files"
            )
        else:
            self.status_bar.show_error("No files with Hebrew text found")

        self.update_files_list()

    def on_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        self.status_bar.show_progress("Scanning directory...")
        self.files_to_process.clear()

        try:
            # Scan directory for MP3 files
            total_files = 0
            hebrew_files = 0

            for root, _, files in os.walk(e.path):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        total_files += 1
                        try:
                            file_path = os.path.join(root, file)
                            self.status_bar.show_progress(f"Processing file {total_files}")

                            mp3_file = MP3File(file_path)
                            print(f"Processing {file_path}")  # Debug logging
                            print(f"Tags: {mp3_file.tags}")  # Debug logging

                            if mp3_file.has_hebrew():
                                self.files_to_process[file_path] = mp3_file
                                hebrew_files += 1
                                print(f"Hebrew found in: {file_path}")  # Debug logging

                        except Exception as error:
                            print(f"Error processing {file_path}: {str(error)}")  # Debug logging
                            continue

            # Update UI
            self.update_files_list()
            if hebrew_files > 0:
                self.status_bar.show_success(
                    f"Found {hebrew_files} files with Hebrew text out of {total_files} MP3 files"
                )
            else:
                self.status_bar.show_error(
                    f"No files with Hebrew text found in {total_files} MP3 files"
                )

        except Exception as error:
            self.status_bar.show_error(f"Error scanning directory: {str(error)}")

    def update_files_list(self):
        """Update the files list display"""
        self.files_list.controls.clear()

        for mp3_file in self.files_to_process.values():
            self.files_list.controls.append(
                FileCard(
                    mp3_file=mp3_file,
                    on_convert=self.convert_file_hebrew,
                    on_remove=self.remove_file,
                    on_selection_change=self._handle_file_selection_change
                )
            )

        self._update_bulk_actions()
        self._update_ui()

    def _handle_select_all(self, e):
        """Handle select all checkbox change"""
        selected = e.value
        for mp3_file in self.files_to_process.values():
            mp3_file.selected = selected
        self.update_files_list()
        self._update_bulk_actions()

    def _handle_convert_selected(self, _):
        """Convert all selected files"""
        converted_count = 0
        for mp3_file in self.files_to_process.values():
            if mp3_file.selected:
                try:
                    mp3_file.convert_hebrew_tags()
                    converted_count += 1
                except Exception as e:
                    print(f"Error converting {mp3_file.path}: {str(e)}")

        if converted_count > 0:
            self.status_bar.show_success(f"Converted {converted_count} files")
        else:
            self.status_bar.show_error("No files selected for conversion")

        self.update_files_list()

    def _handle_save_selected(self, _):
        """Save changes for selected files"""
        selected_files = [
            f for f in self.files_to_process.values()
            if f.selected and f.has_changes()
        ]

        if not selected_files:
            self.status_bar.show_error("No changes to save in selected files")
            return

        DialogBuilder.create_confirmation_dialog(
            page=self.page,
            title="Save Changes",
            content=f"Save changes to {len(selected_files)} selected files?",
            on_confirm=lambda: self._process_save_selected(selected_files),
            confirm_text="Save",
            cancel_text="Cancel"
        )

    def _process_save_selected(self, files_to_save):
        """Process saving changes to selected files"""
        self.status_bar.show_progress("Saving changes...")
        success_count = 0
        failed_files = []

        for mp3_file in files_to_save:
            try:
                if mp3_file.save_changes():
                    success_count += 1
                else:
                    failed_files.append(mp3_file.get_display_path())
            except Exception as e:
                failed_files.append(mp3_file.get_display_path())
                print(f"Error saving {mp3_file.path}: {str(e)}")

        if failed_files:
            self.status_bar.show_error(
                f"Saved {success_count} files. Failed to save: {', '.join(failed_files)}"
            )
        else:
            self.status_bar.show_success(f"Successfully saved {success_count} files")

        self.update_files_list()

    def _handle_file_selection_change(self, mp3_file: MP3File):
        """Handle individual file selection change"""
        self._update_bulk_actions()
        self.select_all_checkbox.value = all(
            f.selected for f in self.files_to_process.values()
        )
        self._update_ui()

    def _update_bulk_actions(self):
        """Update bulk action buttons state"""
        files_selected = any(
            f.selected for f in self.files_to_process.values()
        )
        self.bulk_actions.visible = files_selected

        if files_selected:
            changes_exist = any(
                f.selected and f.has_changes()
                for f in self.files_to_process.values()
            )
            self.bulk_actions.controls[1].disabled = not changes_exist  # Save button

        self._update_ui()

    def convert_file_hebrew(self, mp3_file: MP3File):
        """Convert Hebrew text in file tags"""
        try:
            mp3_file.convert_hebrew_tags()
            self.update_files_list()
            self.status_bar.show_success(f"Converted Hebrew text in {mp3_file.get_display_path()}")
        except Exception as error:
            self.status_bar.show_error(f"Error converting file: {str(error)}")

    def remove_file(self, mp3_file: MP3File):
        """Remove a file from the list"""
        if mp3_file.path in self.files_to_process:
            del self.files_to_process[mp3_file.path]
            self.update_files_list()
            self.status_bar.show_success("File removed")

    def clear_files(self, _):
        """Clear all files"""
        if not self.files_to_process:
            return

        self.files_list.controls.clear()
        self.files_to_process.clear()
        self.select_all_checkbox.value = False
        self.bulk_actions.visible = False
        self.status_bar.show_success("Cleared all files")
        self._update_ui()


def main(page: Page):
    """Initialize and run the application"""
    app = HebrewMP3App(page)


if __name__ == '__main__':
    ft.app(target=main)