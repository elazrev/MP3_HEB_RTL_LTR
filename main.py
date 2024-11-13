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
        self.files_to_process = {}  # Dictionary to store MP3File objects
        self.has_unsaved_changes = False
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
        self.page.window.center()

        # Set theme mode
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=AppTheme.PRIMARY,
            visual_density=ft.VisualDensity.COMFORTABLE
        )

    def initialize_components(self):
        """Initialize UI components"""
        # File pickers
        self.file_picker = ft.FilePicker(on_result=self.on_files_picked)
        self.dir_picker = ft.FilePicker(on_result=self.on_directory_picked)
        self.page.overlay.extend([self.file_picker, self.dir_picker])

        # Status bar
        self.status_bar = StatusBar()

        # Action buttons
        select_files_btn = ft.ElevatedButton(
            text="Select Files",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=['mp3']
            ),
            style=AppTheme.get_button_style(),
            tooltip="Select MP3 files with Hebrew text"
        )

        select_dir_btn = ft.ElevatedButton(
            text="Select Directory",
            icon=ft.icons.FOLDER,
            on_click=lambda _: self.dir_picker.get_directory_path(),
            style=AppTheme.get_button_style(),
            tooltip="Select a directory containing MP3 files"
        )

        clear_btn = ft.ElevatedButton(
            text="Clear All",
            icon=ft.icons.CLEAR_ALL,
            on_click=self.clear_files,
            style=AppTheme.get_button_style(primary=False),
            tooltip="Clear all files from the list"
        )

        self.action_buttons = ft.Container(
            content=ft.Row([
                select_files_btn,
                ft.Container(width=10),
                select_dir_btn,
                ft.Container(width=10),
                clear_btn
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
            on_change=self._handle_select_all,
            label="Select All Files"
        )

        # Convert button
        self.convert_btn = ft.ElevatedButton(
            text="Convert Selected",
            icon=ft.icons.EDIT,
            on_click=self._handle_convert_selected,
            style=AppTheme.get_button_style(),
            tooltip="Convert Hebrew text in selected files",
            disabled=True
        )

        # Save button
        self.save_btn = ft.ElevatedButton(
            text="Save Changes",
            icon=ft.icons.SAVE,
            on_click=self._handle_save_changes,
            style=AppTheme.get_button_style(primary=True),
            tooltip="Save changes to selected files",
            disabled=True
        )

        # Action controls container
        self.action_controls = ft.Container(
            content=ft.Row([
                ft.Row([
                    self.select_all_checkbox,
                    ft.Text(
                        "0 files selected",
                        color=AppTheme.TEXT_SECONDARY,
                        size=14,
                        weight=ft.FontWeight.W_500
                    )
                ]),
                ft.Row([
                    self.convert_btn,
                    ft.Container(width=10),
                    self.save_btn
                ])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            bgcolor=AppTheme.BACKGROUND,
            border_radius=8,
            visible=False  # Initially hidden until files are loaded
        )

    def _update_action_controls(self):
        """Update action controls state"""
        has_files = bool(self.files_to_process)
        has_selected = any(f.selected for f in self.files_to_process.values())
        has_changes = any(f.has_changes() for f in self.files_to_process.values() if f.selected)

        self.action_controls.visible = has_files
        self.convert_btn.disabled = not has_selected
        self.save_btn.disabled = not has_changes

        # Update selected files count
        selected_count = sum(1 for f in self.files_to_process.values() if f.selected)
        self.action_controls.content.controls[0].controls[1].value = f"{selected_count} files selected"

        if self.page:
            self.page.update()

    def _update_ui(self):
        """Update UI safely"""
        # עדכון כאן
        if self.save_button:
            self.save_button.disabled = not self.has_unsaved_changes
        self._update_file_count()
        if self.page:
            self.page.update()

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

        # Files section with controls
        files_section = ft.Container(
            content=ft.Column([
                # Section header with file count
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
                        ft.Text(
                            f"{self._get_selected_count()} selected",
                            color=AppTheme.TEXT_SECONDARY,
                            size=14
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.only(bottom=12)
                ),

                # Action buttons
                ft.Container(
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
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=10
                ),

                # Selection and action controls
                ft.Container(
                    content=ft.Row([
                        # Select all checkbox
                        ft.Checkbox(
                            ref=self.select_all_checkbox,
                            label="Select All",
                            value=False,
                            on_change=self._handle_select_all
                        ),
                        # Action buttons
                        ft.Row([
                            ft.ElevatedButton(
                                text="Convert Selected",
                                icon=ft.icons.EDIT,
                                on_click=self._handle_convert_selected,
                                style=AppTheme.get_button_style(),
                                tooltip="Convert Hebrew text in selected files"
                            ),
                            ft.Container(width=10),
                            ft.ElevatedButton(
                                text="Save Changes",
                                icon=ft.icons.SAVE,
                                on_click=self._handle_save_changes,
                                style=AppTheme.get_button_style(primary=True),
                                tooltip="Save changes to selected files"
                            )
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    visible=bool(self.files_to_process)
                ),

                # Status bar
                self.status_bar,

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
            files_section,
            footer
        )

    def _update_ui(self):
        """Update UI safely"""
        if self.page:
            self.page.update()

    def _update_file_count(self):
        """Update the file count and unsaved changes indicator"""
        selected_count = sum(1 for f in self.files_to_process.values() if f.selected)
        total_count = len(self.files_to_process)
        self.has_unsaved_changes = any(
            f.has_changes() for f in self.files_to_process.values() if f.selected
        )

    def on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        # Clear existing files when selecting new files
        self.files_to_process.clear()
        self.status_bar.show_progress(f"Processing {len(e.files)} files...")

        hebrew_files_count = 0
        for f in e.files:
            try:
                mp3_file = MP3File(f.path)
                if mp3_file.has_hebrew():
                    self.files_to_process[f.path] = mp3_file
                    hebrew_files_count += 1
            except Exception:
                continue

        self.update_files_list()
        if hebrew_files_count > 0:
            self.status_bar.show_success(
                f"Found {hebrew_files_count} files with Hebrew text"
            )
        else:
            self.status_bar.show_error("No files with Hebrew text found")

    def on_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        try:
            self.status_bar.show_progress("Scanning directory...")
            self.files_to_process.clear()

            # Scan directory for MP3 files
            total_files = 0
            hebrew_files = 0

            # Use os.walk with error handling
            for root, _, files in os.walk(e.path, onerror=None):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        try:
                            total_files += 1
                            file_path = os.path.join(root, file)
                            self.status_bar.show_progress(f"Processing file {total_files}")

                            # Check if file is accessible
                            if not os.access(file_path, os.R_OK):
                                continue

                            mp3_file = MP3File(file_path)
                            if mp3_file and mp3_file.has_hebrew():
                                self.files_to_process[file_path] = mp3_file
                                hebrew_files += 1

                        except (PermissionError, OSError):
                            continue
                        except Exception:
                            continue

            # Update UI
            self.update_files_list()

            # Show results
            if hebrew_files > 0:
                self.status_bar.show_success(
                    f"Found {hebrew_files} files with Hebrew text out of {total_files} MP3 files"
                )
            else:
                if total_files > 0:
                    self.status_bar.show_error(
                        f"No files with Hebrew text found in {total_files} MP3 files"
                    )
                else:
                    self.status_bar.show_error("No MP3 files found in directory")

        except PermissionError:
            self.status_bar.show_error("Access denied to directory")
        except Exception as error:
            self.status_bar.show_error(f"Error scanning directory: {str(error)}")
        finally:
            self._update_ui()

    def _update_file_count(self):
        """Update file count display"""
        selected_count = sum(1 for f in self.files_to_process.values() if f.selected)
        total_count = len(self.files_to_process)

        if total_count > 0:
            if selected_count == total_count:
                self.select_all_checkbox.value = True
            elif selected_count == 0:
                self.select_all_checkbox.value = False

    def update_files_list(self):
        """Update the files list display"""
        self.files_list.controls.clear()

        for mp3_file in self.files_to_process.values():
            card = FileCard(
                mp3_file=mp3_file,
                on_convert=self.convert_file_hebrew,
                on_remove=self.remove_file,
                on_selection_change=self._handle_file_selection_change
            )
            self.files_list.controls.append(card)

        self._update_ui()

    def _handle_file_selection_change(self, mp3_file: MP3File):
        """Handle individual file selection change"""
        if self.page:
            all_selected = all(f.selected for f in self.files_to_process.values())
            self.select_all_checkbox.value = all_selected
            self._update_ui()

    def _get_selected_count(self) -> int:
        """Get count of selected files"""
        return sum(1 for f in self.files_to_process.values() if f.selected)

    def _handle_select_all(self, e):
        """Handle select all checkbox change"""
        selected = e.control.value
        for mp3_file in self.files_to_process.values():
            mp3_file.selected = selected
        self.update_files_list()
        self._update_ui()

    def _handle_file_selection_change(self, mp3_file: MP3File):
        """Handle individual file selection change"""
        self._update_ui()
        self.select_all_checkbox.value = all(
            f.selected for f in self.files_to_process.values()
        )

    def convert_file_hebrew(self, mp3_file: MP3File):
        """Convert Hebrew text in file tags"""
        try:
            mp3_file.convert_hebrew_tags()
            self.has_unsaved_changes = True
            self.update_files_list()
            self.status_bar.show_success(f"Converted Hebrew text in {mp3_file.get_display_path()}")
        except Exception as error:
            self.status_bar.show_error(f"Error converting file: {mp3_file.get_display_path()}")

    def _handle_convert_selected(self, _):
        """Convert Hebrew text in selected files"""
        selected_files = [f for f in self.files_to_process.values() if f.selected]
        if not selected_files:
            self.status_bar.show_error("No files selected")
            return

        converted_count = 0
        for mp3_file in selected_files:
            try:
                mp3_file.convert_hebrew_tags()
                converted_count += 1
                self.has_unsaved_changes = True
            except Exception as e:
                self.status_bar.show_error(f"Error converting {mp3_file.get_display_path()}")
                continue

        if converted_count > 0:
            self.status_bar.show_success(f"Converted {converted_count} files")
            self.update_files_list()

    def _handle_save_changes(self, _):
        """Save changes to selected files"""
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
            on_confirm=lambda: self._process_save_changes(selected_files),
            confirm_text="Save",
            cancel_text="Cancel"
        )

    def _process_save_changes(self, files_to_save):
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
            self.has_unsaved_changes = False

        self.update_files_list()

    def remove_file(self, mp3_file: MP3File):
        """Remove a file from the list"""
        if mp3_file.path in self.files_to_process:
            del self.files_to_process[mp3_file.path]
            self.update_files_list()
            self.status_bar.show_success(f"Removed {mp3_file.get_display_path()}")

    def clear_files(self, _):
        """Clear all files"""
        if not self.files_to_process:
            return

        if self.has_unsaved_changes:
            DialogBuilder.create_confirmation_dialog(
                page=self.page,
                title="Clear Files",
                content="There are unsaved changes. Are you sure you want to clear all files?",
                on_confirm=self._process_clear_files,
                confirm_text="Clear",
                cancel_text="Cancel",
                danger=True
            )
        else:
            self._process_clear_files()

    def _process_clear_files(self):
        """Process clearing all files"""
        self.files_to_process.clear()
        self.files_list.controls.clear()
        self.has_unsaved_changes = False
        self.select_all_checkbox.value = False
        self.status_bar.show_success("Cleared all files")
        self._update_ui()


def main(page: Page):
    """Initialize and run the application"""
    HebrewMP3App(page)


if __name__ == '__main__':
    ft.app(target=main)