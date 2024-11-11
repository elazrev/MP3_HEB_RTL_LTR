import flet as ft
from flet import Page
from src.models.mp3_file import MP3File
from src.ui.components.file_card import FileCard
from src.ui.components.status_bar import StatusBar
from src.ui.components.toolbar import Toolbar
from src.ui.components.dialog_builder import DialogBuilder
from src.ui.styles import AppTheme, AppAnimations
import os


class HebrewMP3App:
    def __init__(self, page: Page):
        self.page = page
        self.files_to_process = {}  # Dictionary to store MP3File objects
        self.setup_page()
        self.initialize_components()
        self.build_ui()

    def setup_page(self):
        """Configure the page settings"""
        self.page.title = "Hebrew MP3 Tag Fixer"
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.padding = 20
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = AppTheme.BACKGROUND
        self.page.auto_scroll = True

    def initialize_components(self):
        """Initialize UI components"""
        # File pickers
        self.file_picker = ft.FilePicker(on_result=self.on_files_picked)
        self.dir_picker = ft.FilePicker(on_result=self.on_directory_picked)
        self.page.overlay.extend([self.file_picker, self.dir_picker])

        # Status bar
        self.status_bar = StatusBar()

        # Files list
        self.files_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=10,
            height=400
        )

        # Selection controls
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            value=False,
            on_change=self._handle_select_all
        )

        # Bulk action buttons
        self.bulk_actions = ft.Row([
            ft.ElevatedButton(
                "Convert Selected",
                icon=ft.icons.EDIT,
                on_click=self._handle_convert_selected,
                disabled=True
            ),
            ft.ElevatedButton(
                "Save Changes",
                icon=ft.icons.SAVE,
                on_click=self._handle_save_selected,
                disabled=True
            )
        ], visible=False)

    def build_ui(self):
        """Build the main UI"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Hebrew MP3 Tag Fixer",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=AppTheme.TEXT_PRIMARY
                ),
                ft.Text(
                    "by elaz.rev",
                    size=12,
                    italic=True,
                    color=AppTheme.TEXT_SECONDARY
                )
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=AppTheme.PADDING_MEDIUM)
        )

        # Action Buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Select Files",
                icon=ft.icons.FOLDER_OPEN,
                on_click=lambda _: self.file_picker.pick_files(
                    allow_multiple=True,
                    allowed_extensions=['mp3']
                )
            ),
            ft.ElevatedButton(
                "Select Directory",
                icon=ft.icons.FOLDER,
                on_click=lambda _: self.dir_picker.get_directory_path()
            ),
            ft.ElevatedButton(
                "Clear All",
                icon=ft.icons.CLEAR_ALL,
                on_click=self.clear_files
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Files section
        files_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "Files with Hebrew",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.TEXT_PRIMARY
                    ),
                    ft.Text(
                        f"({len(self.files_to_process)} files)",
                        color=AppTheme.TEXT_SECONDARY,
                        size=14
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Selection controls
                ft.Row([
                    self.select_all_checkbox,
                    self.bulk_actions
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                self.files_list
            ]),
            padding=ft.padding.symmetric(vertical=AppTheme.PADDING_SMALL)
        )

        # Add components to page
        self.page.add(
            header,
            action_buttons,
            self.status_bar,
            files_section
        )

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
                mp3_file.convert_hebrew_tags()
                converted_count += 1

        if converted_count > 0:
            self.status_bar.show_success(f"Converted {converted_count} files")
        else:
            self.status_bar.show_error("No files selected")

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
        self.update()

    def _update_bulk_actions(self):
        """Update bulk action buttons state"""
        files_selected = any(
            f.selected for f in self.files_to_process.values()
        )
        self.bulk_actions.visible = files_selected

        if files_selected:
            has_changes = any(
                f.selected and f.has_changes()
                for f in self.files_to_process.values()
            )
            self.bulk_actions.controls[1].disabled = not has_changes

        self.update()

    def clear_files(self, _):
        """Clear all files"""
        if not self.files_to_process:
            return

        self.files_to_process.clear()
        self.files_list.controls.clear()
        self.select_all_checkbox.value = False
        self.bulk_actions.visible = False
        self.status_bar.show_success("Cleared all files")
        self.page.update()

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
        self.page.update()

    def on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        self.status_bar.show_progress(f"Processing {len(e.files)} files...")

        # Process files
        for f in e.files:
            try:
                mp3_file = MP3File(f.path)
                self.files_to_process[f.path] = mp3_file
            except Exception as error:
                self.status_bar.show_error(f"Error processing {f.name}: {str(error)}")

        # Update UI
        self.update_files_list()
        self.status_bar.show_success(f"Loaded {len(e.files)} files")

    def on_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        self.status_bar.show_progress("Scanning directory...")

        try:
            # Scan directory for MP3 files
            mp3_files = []
            for root, _, files in os.walk(e.path):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        mp3_files.append(os.path.join(root, file))

            # Process files
            for file_path in mp3_files:
                try:
                    mp3_file = MP3File(file_path)
                    self.files_to_process[file_path] = mp3_file
                except Exception as error:
                    self.status_bar.show_error(f"Error processing {file_path}")

            # Update UI
            self.update_files_list()
            self.status_bar.show_success(f"Found {len(mp3_files)} MP3 files")

        except Exception as error:
            self.status_bar.show_error(f"Error scanning directory: {str(error)}")

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

        DialogBuilder.create_confirmation_dialog(
            page=self.page,
            title="Clear All Files",
            content="Are you sure you want to clear all files from the list?",
            on_confirm=self._do_clear_files,
            confirm_text="Clear",
            cancel_text="Cancel",
            danger=True
        )

    def _do_clear_files(self):
        """Actually clear all files after confirmation"""
        self.files_to_process.clear()
        self.update_files_list()
        self.status_bar.show_success("Cleared all files")

    def has_unsaved_changes(self) -> bool:
        """Check if there are any unsaved changes"""
        return any(
            mp3_file.has_changes()
            for mp3_file in self.files_to_process.values()
        )

    def save_all_changes(self, _):
        """Save changes to all files"""
        files_with_changes = [
            f for f in self.files_to_process.values()
            if f.has_changes()
        ]

        if not files_with_changes:
            self.status_bar.show_success("No changes to save")
            return

        DialogBuilder.create_confirmation_dialog(
            page=self.page,
            title="Save Changes",
            content=f"Save changes to {len(files_with_changes)} files?",
            on_confirm=self.process_save_changes,
            confirm_text="Save",
            cancel_text="Cancel"
        )

    def process_save_changes(self):
        """Process saving changes to files"""
        self.status_bar.show_progress("Saving changes...")
        success_count = 0
        failed_files = []

        for mp3_file in self.files_to_process.values():
            if mp3_file.has_changes():
                try:
                    if mp3_file.save_changes():
                        success_count += 1
                    else:
                        failed_files.append(mp3_file.get_display_path())
                except Exception as e:
                    failed_files.append(mp3_file.get_display_path())

        # Update status
        if failed_files:
            self.status_bar.show_error(
                f"Saved {success_count} files. Failed to save: "
                f"{', '.join(failed_files)}"
            )
        else:
            self.status_bar.show_success(f"Successfully saved changes to {success_count} files")

        # Update UI
        self.update_files_list()


def main(page: Page):
    app = HebrewMP3App(page)


if __name__ == '__main__':
    ft.app(target=main)