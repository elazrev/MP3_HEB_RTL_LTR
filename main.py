import flet as ft
from flet import Page
from src.models.mp3_file import MP3File
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

    def initialize_components(self):
        """Initialize UI components"""
        # File pickers
        self.file_picker = ft.FilePicker(on_result=self.on_files_picked)
        self.dir_picker = ft.FilePicker(on_result=self.on_directory_picked)
        self.page.overlay.extend([self.file_picker, self.dir_picker])

        # Status text
        self.status_text = ft.Text(
            size=16,
            weight=ft.FontWeight.NORMAL
        )

        # Files list
        self.files_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            height=400
        )

    def build_ui(self):
        """Build the main UI"""
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Hebrew MP3 Tag Fixer",
                    size=32,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "by elaz.rev",
                    size=16,
                    italic=True
                )
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(bottom=20)
        )

        # Action buttons
        select_files_btn = ft.ElevatedButton(
            "Select MP3 Files",
            icon=ft.icons.FOLDER_OPEN,
            on_click=lambda _: self.file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=['mp3']
            )
        )

        select_dir_btn = ft.ElevatedButton(
            "Select Directory",
            icon=ft.icons.FOLDER,
            on_click=lambda _: self.dir_picker.get_directory_path()
        )

        clear_btn = ft.ElevatedButton(
            "Clear",
            icon=ft.icons.CLEAR_ALL,
            on_click=self.clear_files
        )

        # Add components to page
        self.page.add(
            header,
            ft.Row(
                [select_files_btn, select_dir_btn, clear_btn],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            self.status_text,
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Files to Process", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"({len(self.files_to_process)} files)")
                    ]),
                    self.files_list
                ]),
                margin=ft.margin.only(top=20)
            )
        )

    def create_file_tile(self, mp3_file: MP3File) -> ft.ListTile:
        """Create a ListTile for an MP3 file"""
        # Show original and converted values if has Hebrew
        if mp3_file.has_hebrew():
            title_preview = mp3_file.get_tag_preview('title')
            artist_preview = mp3_file.get_tag_preview('artist')
            album_preview = mp3_file.get_tag_preview('album')

            return ft.ListTile(
                leading=ft.Icon(ft.icons.MUSIC_NOTE),
                title=ft.Column([
                    ft.Text(title_preview['original'],
                            color="grey400",
                            text_decoration=ft.TextDecoration.LINE_THROUGH),
                    ft.Text(title_preview['converted'], color="blue400")
                ]),
                subtitle=ft.Column([
                    ft.Row([
                        ft.Text("Artist: ", size=12),
                        ft.Text(artist_preview['original'],
                                color="grey400",
                                text_decoration=ft.TextDecoration.LINE_THROUGH if artist_preview['analysis'][
                                    'contains_hebrew'] else None),
                        ft.Text(" → ", color="grey400") if artist_preview['analysis']['contains_hebrew'] else ft.Text(
                            ""),
                        ft.Text(artist_preview['converted'], color="blue400") if artist_preview['analysis'][
                            'contains_hebrew'] else ft.Text("")
                    ]),
                    ft.Row([
                        ft.Text("Album: ", size=12),
                        ft.Text(album_preview['original'],
                                color="grey400",
                                text_decoration=ft.TextDecoration.LINE_THROUGH if album_preview['analysis'][
                                    'contains_hebrew'] else None),
                        ft.Text(" → ", color="grey400") if album_preview['analysis']['contains_hebrew'] else ft.Text(
                            ""),
                        ft.Text(album_preview['converted'], color="blue400") if album_preview['analysis'][
                            'contains_hebrew'] else ft.Text("")
                    ])
                ]),
                trailing=ft.Row([
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        tooltip="Convert Hebrew",
                        on_click=lambda e: self.convert_file_hebrew(mp3_file)
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        icon_color="red400",
                        tooltip="Remove file",
                        on_click=lambda e: self.remove_file(mp3_file.path)
                    )
                ])
            )
        else:
            # Simple display for files without Hebrew
            return ft.ListTile(
                leading=ft.Icon(ft.icons.MUSIC_NOTE),
                title=ft.Text(mp3_file.tags['title'] or mp3_file.get_display_path()),
                subtitle=ft.Column([
                    ft.Text(f"Artist: {mp3_file.tags['artist']}" if mp3_file.tags['artist'] else "No artist"),
                    ft.Text(f"Album: {mp3_file.tags['album']}" if mp3_file.tags['album'] else "No album")
                ]),
                trailing=ft.IconButton(
                    icon=ft.icons.DELETE,
                    icon_color="red400",
                    tooltip="Remove file",
                    on_click=lambda e: self.remove_file(mp3_file.path)
                )
            )

        def convert_file_hebrew(self, mp3_file: MP3File):
            """Convert Hebrew text in file tags"""
            mp3_file.convert_hebrew_tags()
            self.update_files_list()
            self.status_text.value = f"Converted Hebrew text in {mp3_file.get_display_path()}"
            self.page.update()

    def on_files_picked(self, e: ft.FilePickerResultEvent):
        """Handle files being picked"""
        if not e.files:
            return

        self.status_text.value = f"Processing {len(e.files)} files..."
        self.page.update()

        # Process files
        for f in e.files:
            try:
                mp3_file = MP3File(f.path)
                self.files_to_process[f.path] = mp3_file
            except Exception as error:
                print(f"Error processing {f.name}: {str(error)}")

        # Update UI
        self.update_files_list()
        self.status_text.value = f"Loaded {len(e.files)} files"
        self.page.update()

    def on_directory_picked(self, e: ft.FilePickerResultEvent):
        """Handle directory being picked"""
        if not e.path:
            return

        self.status_text.value = "Scanning directory..."
        self.page.update()

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
                print(f"Error processing {file_path}: {str(error)}")

        # Update UI
        self.update_files_list()
        self.status_text.value = f"Found {len(mp3_files)} MP3 files"
        self.page.update()

    def update_files_list(self):
        """Update the files list display"""
        self.files_list.controls.clear()
        for mp3_file in self.files_to_process.values():
            self.files_list.controls.append(self.create_file_tile(mp3_file))

    def remove_file(self, file_path: str):
        """Remove a file from the list"""
        if file_path in self.files_to_process:
            del self.files_to_process[file_path]
            self.update_files_list()
            self.status_text.value = "File removed"
            self.page.update()

    def clear_files(self, _):
        """Clear all files"""
        self.files_to_process.clear()
        self.files_list.controls.clear()
        self.status_text.value = "Cleared all files"
        self.page.update()

def main(page: Page):
    HebrewMP3App(page)

if __name__ == '__main__':
    ft.app(target=main)