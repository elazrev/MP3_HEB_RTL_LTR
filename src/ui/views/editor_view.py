import flet as ft
from typing import Optional
from ...models.hebrew_fixer import HebrewFixer
from ..components.action_buttons import ActionButtons
from ..components.status_bar import StatusBar
from ..components.file_preview import FilePreviewCard
from ..widgets.dialog_builder import DialogBuilder

class EditorView(ft.UserControl):
    def __init__(self, fixer: HebrewFixer):
        super().__init__()
        self.fixer = fixer
        self.pick_files_dialog: Optional[ft.FilePicker] = None
        self.pick_directory_dialog: Optional[ft.FilePicker] = None
        self._initialize_components()

    def _initialize_components(self):
        self.status_bar = StatusBar()
        self.files_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=500,
            auto_scroll=True
        )
        self.action_buttons = ActionButtons(
            on_select_files=self._handle_select_files,
            on_select_directory=self._handle_select_directory,
            on_clear=self._handle_clear_screen
        )

    def build(self):
        return ft.Column([
            self.action_buttons,
            self.status_bar,
            self.files_list,
            self._build_bottom_buttons(),
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_bottom_buttons(self):
        return ft.Row([
            ft.ElevatedButton(
                text="Save Changes",
                icon=ft.icons.SAVE,
                on_click=self._handle_save_changes,
                disabled=len(self.fixer.files_to_process) == 0,
            ),
            ft.Container(width=10),
            ft.ElevatedButton(
                text="Undo Last Change",
                icon=ft.icons.UNDO,
                on_click=self._handle_undo,
                disabled=len(self.fixer.history) == 0,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

    def initialize_pickers(self):
        """Initialize file pickers after the view is mounted"""
        if not self.page:
            return

        self.pick_files_dialog = ft.FilePicker(
            on_result=self._handle_files_picked
        )
        self.pick_directory_dialog = ft.FilePicker(
            on_result=self._handle_directory_picked
        )

        self.page.overlay.extend([
            self.pick_files_dialog,
            self.pick_directory_dialog
        ])
        self.page.update()

    def _handle_select_files(self, _):
        """Handle select files button click"""
        if self.pick_files_dialog:
            self.pick_files_dialog.pick_files(
                allow_multiple=True,
                allowed_extensions=['mp3'],
                dialog_title="Select MP3 Files"
            )

    def _handle_select_directory(self, _):
        """Handle select directory button click"""
        if self.pick_directory_dialog:
            self.pick_directory_dialog.get_directory_path(
                dialog_title="Select Directory with MP3 Files"
            )

    def _handle_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        self.status_bar.show_progress(f"Processing {len(e.files)} files...")
        self.files_list.controls.clear()
        self.fixer.files_to_process.clear()

        processed_count = 0
        for f in e.files:
            try:
                mp3_file = self.fixer.process_file(f.path)
                if mp3_file.has_changes():  # Only add files with Hebrew text
                    self.fixer.files_to_process[f.path] = mp3_file
                    self.files_list.controls.append(
                        FilePreviewCard(
                            mp3_file,
                            on_remove=self._handle_file_remove
                        )
                    )
                    processed_count += 1
            except Exception as error:
                self.status_bar.show_error(f"Error processing {f.name}: {str(error)}")
                continue

        if processed_count > 0:
            self.status_bar.show_success(
                f"Found {processed_count} files with Hebrew text"
            )
        else:
            self.status_bar.show_success("No files with Hebrew text found")

        self.update()

    def _handle_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        self.status_bar.show_progress("Scanning directory...")
        files = self.fixer.scan_directory(e.path)

        if not files:
            self.status_bar.show_success("No MP3 files found in directory")
            return

        self.files_list.controls.clear()
        self.fixer.files_to_process.clear()

        hebrew_files_count = 0
        for mp3_file in files:
            try:
                if mp3_file.has_changes():  # Only add files with Hebrew text
                    self.fixer.files_to_process[mp3_file.path] = mp3_file
                    self.files_list.controls.append(
                        FilePreviewCard(
                            mp3_file,
                            on_remove=self._handle_file_remove
                        )
                    )
                    hebrew_files_count += 1
            except Exception as error:
                self.status_bar.show_error(f"Error processing file: {str(error)}")
                continue

        if hebrew_files_count > 0:
            self.status_bar.show_success(
                f"Found {hebrew_files_count} files with Hebrew text out of {len(files)} MP3 files"
            )
        else:
            self.status_bar.show_success(f"No files with Hebrew text found in {len(files)} MP3 files")

        self.update()

    def _handle_clear_screen(self, _):
        """Handle clear screen button click"""
        self.files_list.controls.clear()
        self.fixer.files_to_process.clear()
        self.status_bar.show_success("Screen cleared")
        self.update()

    def _handle_file_remove(self, mp3_file):
        """Handle file being removed from the list"""
        if mp3_file.path in self.fixer.files_to_process:
            del self.fixer.files_to_process[mp3_file.path]
            self.files_list.controls = [
                control for control in self.files_list.controls
                if isinstance(control, FilePreviewCard)
                   and control.mp3_file.path != mp3_file.path
            ]
            self.status_bar.show_success(f"Removed: {mp3_file.get_display_path()}")
            self.update()

    def _handle_save_changes(self, _):
        """Handle save changes button click"""
        if not self.fixer.files_to_process:
            self.status_bar.show_error("No files to process")
            return

        DialogBuilder.create_confirmation_dialog(
            page=self.page,
            title="Save Changes",
            content=f"Save changes to {len(self.fixer.files_to_process)} files?",
            on_confirm=self._process_save,
            confirm_text="Save",
            cancel_text="Cancel"
        )

    def _process_save(self, _):
        """Process the actual saving of files"""
        try:
            self.status_bar.show_progress("Saving changes...")
            success_count = 0

            for mp3_file in self.fixer.files_to_process.values():
                try:
                    if self.fixer.save_changes(mp3_file):
                        success_count += 1
                except Exception as save_error:
                    self.status_bar.show_error(f"Error saving {mp3_file.path}: {str(save_error)}")
                    continue

            self.status_bar.show_success(f"Successfully processed {success_count} files")
            self.files_list.controls.clear()
            self.fixer.files_to_process.clear()
            self.update()

        except Exception as e:
            self.status_bar.show_error(f"Error saving changes: {str(e)}")

    def _handle_undo(self, _):
        """Handle undo button click"""
        if not self.fixer.history:
            self.status_bar.show_error("No changes to undo")
            return

        DialogBuilder.create_confirmation_dialog(
            page=self.page,
            title="Undo Last Change",
            content="Are you sure you want to undo the last change?",
            on_confirm=self._process_undo,
            confirm_text="Undo",
            cancel_text="Cancel",
            danger=True
        )

    def _process_undo(self, _):
        """Process the actual undo operation"""
        try:
            self.status_bar.show_progress("Undoing last change...")

            if self.fixer.undo_last_change():
                self.status_bar.show_success("Last change undone")
            else:
                self.status_bar.show_error("Failed to undo last change")

            self.update()

        except Exception as e:
            self.status_bar.show_error(f"Error undoing changes: {str(e)}")