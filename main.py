import flet as ft
from click import style
from flet import Page
from src.models.mp3_file import MP3File
from src.ui.components.file_card import FileCard
from src.ui.components.status_bar import StatusBar
from src.ui.components.toolbar import Toolbar
from src.ui.components.contact_dialog import ContactManager
from src.ui.styles import AppTheme, AppInfo
import os

VERSION = AppInfo.VERSION

class HebrewMP3App:
    def __init__(self, page: Page):
        self.page = page
        self.files_to_process = {}
        self.contact_manager = ContactManager(page)  # יצירת מנהל הקשר
        self.setup_page()
        self.initialize_components()
        self.build_ui()

    def setup_page(self):
        """Configure the page settings"""
        self.page.title = "Hebrew MP3 Tag Fixer"
        self.page.window.width = 900  # חלון קטן יותר
        self.page.window.height = 700
        self.page.padding = 10  # מרווחים קטנים יותר
        self.page.theme_mode = ft.ThemeMode.LIGHT  # מצב בהיר
        self.page.bgcolor = "#FFFFFF"  # רקע לבן

        # הגדרת ScrollMode כך שיאפשר גלילה מלאה
        self.page.scroll = ft.ScrollMode.AUTO

    def initialize_components(self):
        """Initialize UI components"""
        # File pickers
        self.file_picker = ft.FilePicker(on_result=self._handle_files_picked)
        self.dir_picker = ft.FilePicker(on_result=self._handle_directory_picked)
        self.page.overlay.extend([self.file_picker, self.dir_picker])

        # Status bar
        self.status_bar = StatusBar()

        # Toolbar with all callbacks
        self.toolbar = Toolbar(
            on_select_files=lambda _: self.file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=['mp3']
            ),
            on_select_directory=lambda _: self.dir_picker.get_directory_path(),
            on_clear=self._handle_clear,
            on_save_selected=self._handle_save_selected,
            on_convert_selected=self._handle_convert_selected
        )

        # Files list with infinite scroll
        self.files_list = ft.ListView(
            expand=True,
            spacing=5,  # מרווח קטן יותר בין פריטים
            padding=5,
            auto_scroll=True,
            height=350  # גובה קבוע
        )

        # Select all controls
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            value=False,
            on_change=self._handle_select_all,
            scale=0.9  # קטן יותר
        )

        # Footer
        self.footer = ft.Container(
            content=ft.Text(
                f"Version {VERSION}",
                size=12,
                color="#666666",
                italic=True
            ),
            padding=5,
            alignment=ft.alignment.center
        )

    def _handle_convert_selected(self, _):
        """Handle converting selected files"""
        selected_files = [
            f for f in self.files_to_process.values()
            if f.selected
        ]

        if not selected_files:
            self.status_bar.show_error("No files selected")
            return

        converted_count = 0
        for mp3_file in selected_files:
            try:
                mp3_file.convert_hebrew_tags()
                converted_count += 1
            except Exception as e:
                print(f"Error converting {mp3_file.path}: {str(e)}")

        if converted_count > 0:
            self.status_bar.show_success(f"Converted {converted_count} files")
            self.update_files_list()
        else:
            self.status_bar.show_error("No files were converted")

    def _handle_select_all(self, e):
        """Handle select all checkbox change"""
        selected = e.data == "true"
        for mp3_file in self.files_to_process.values():
            mp3_file.selected = selected
        self.update_files_list()
        self._update_toolbar_state()

    def _handle_save_selected(self, _):
        """Handle saving selected files"""
        selected_files = [
            f for f in self.files_to_process.values()
            if f.selected and f.has_changes()
        ]

        if not selected_files:
            self.status_bar.show_error("No changes to save in selected files")
            return

        # Show confirmation dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Save {len(selected_files)} Files?"),
            content=ft.Text("This will modify the selected files. Continue?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self._close_dialog(dialog)),
                ft.TextButton("Save", on_click=lambda e: self._process_save_selected(dialog, selected_files)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _process_save_selected(self, dialog, files_to_save):
        """Process saving the selected files"""
        dialog.open = False
        self.page.update()

        self.status_bar.show_progress(f"Saving {len(files_to_save)} files...")

        success_count = 0
        failed_files = []

        for mp3_file in files_to_save:
            try:
                if mp3_file.save_changes():
                    success_count += 1
                else:
                    failed_files.append(mp3_file.get_display_path())
            except Exception as e:
                print(f"Error saving {mp3_file.path}: {str(e)}")
                failed_files.append(mp3_file.get_display_path())

        if failed_files:
            self.status_bar.show_error(
                f"Saved {success_count} files. Failed to save: {', '.join(failed_files)}"
            )
        else:
            self.status_bar.show_success(f"Successfully saved {success_count} files")

        self.update_files_list()

    def _close_dialog(self, dialog):
        """Close dialog"""
        dialog.open = False
        self.page.update()

    def _handle_clear(self, _):
        """Clear all files"""
        if not self.files_to_process:
            return

        self.files_to_process.clear()
        self.files_list.controls.clear()
        self.select_all_checkbox.value = False
        self._update_toolbar_state()
        self.status_bar.show_success("Cleared all files")
        self.page.update()

    def update_files_list(self):
        """Update the files list display"""
        self.files_list.controls.clear()

        for mp3_file in self.files_to_process.values():
            self.files_list.controls.append(
                FileCard(
                    mp3_file=mp3_file,
                    on_convert=self._handle_convert,
                    on_remove=self._handle_remove,
                    on_selection_change=self._handle_file_selection_change
                )
            )

        self._update_toolbar_state()
        self.page.update()

    def _update_toolbar_state(self):
        """Update toolbar buttons state"""
        has_selected = any(f.selected for f in self.files_to_process.values())
        has_changes = any(
            f.selected and f.has_changes()
            for f in self.files_to_process.values()
        )

        self.toolbar.update_buttons_state(has_selected, has_changes)

    def _handle_convert(self, mp3_file: MP3File):
        """Handle converting a file's Hebrew text"""
        mp3_file.convert_hebrew_tags()
        self.update_files_list()
        self.status_bar.show_success(f"Converted Hebrew text in {mp3_file.get_display_path()}")

    def _handle_remove(self, mp3_file: MP3File):
        """Handle removing a file from the list"""
        if mp3_file.path in self.files_to_process:
            del self.files_to_process[mp3_file.path]
            self.update_files_list()
            self.status_bar.show_success("File removed")

    def _handle_file_selection_change(self, mp3_file: MP3File):
        """Handle when a file's selection changes"""
        self._update_toolbar_state()

        # Update "Select All" checkbox state
        all_selected = all(f.selected for f in self.files_to_process.values())
        self.select_all_checkbox.value = all_selected
        self.page.update()

    def build_ui(self):
        """Build the main UI"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Hebrew MP3 Tag Fixer",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color="#2E2E2E"
                ),
                ft.Row(
                    [
                        ft.Text(
                            "by ",
                            size=12,
                            italic=True,
                            color="#666666"
                        ),
                        self.contact_manager.create_contact_button()  # שימוש במנהל הקשר
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ], spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.only(bottom=5)
        )

        # Files section
        files_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(
                        "Files with Hebrew",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color="#2E2E2E"
                    ),
                    ft.Text(
                        f"({len(self.files_to_process)} files)",
                        color="#666666",
                        size=12
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([
                    self.select_all_checkbox
                ], alignment=ft.MainAxisAlignment.START),

                # Files list בתוך Container שמאפשר גלילה
                ft.Container(
                    content=self.files_list,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=5,
                    padding=5
                )
            ]),
            padding=5,
            expand=True  # חשוב לגלילה
        )

        # Main content layout
        main_content = ft.Column([
            header,
            self.toolbar,
            self.status_bar,
            files_section
        ], expand=True)

        # Add everything to page
        self.page.add(
            main_content,
            ft.Divider(height=1, color="#E0E0E0"),  # קו מפריד לפני ה-footer
            self.footer
        )

    def _handle_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        self.status_bar.show_progress(f"Processing {len(e.files)} files...")

        # Clear existing files when selecting new ones
        self.files_to_process.clear()
        self.files_list.controls.clear()

        # Process files
        hebrew_files_count = 0
        for f in e.files:
            try:
                mp3_file = MP3File(f.path)
                if mp3_file.has_hebrew():
                    self.files_to_process[f.path] = mp3_file
                    hebrew_files_count += 1
            except Exception as error:
                self.status_bar.show_error(f"Error processing {f.name}")
                print(f"Error details: {str(error)}")

        self.update_files_list()
        self.status_bar.show_success(
            f"Found {hebrew_files_count} files with Hebrew text"
        )

    def _handle_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        self.status_bar.show_progress("Scanning directory...")

        try:
            # Clear existing files
            self.files_to_process.clear()
            self.files_list.controls.clear()

            # Scan directory for MP3 files
            total_files = 0
            hebrew_files = 0

            for root, _, files in os.walk(e.path):
                for file in files:
                    if file.lower().endswith('.mp3'):
                        total_files += 1
                        try:
                            file_path = os.path.join(root, file)
                            mp3_file = MP3File(file_path)
                            if mp3_file.has_hebrew():
                                self.files_to_process[file_path] = mp3_file
                                hebrew_files += 1
                        except Exception as error:
                            print(f"Error processing {file}: {str(error)}")
                            continue

            self.update_files_list()
            self.status_bar.show_success(
                f"Found {hebrew_files} files with Hebrew text out of {total_files} MP3 files"
            )

        except Exception as error:
            self.status_bar.show_error(f"Error scanning directory: {str(error)}")


def main(page: Page):
    HebrewMP3App(page)


if __name__ == '__main__':
    ft.app(target=main)