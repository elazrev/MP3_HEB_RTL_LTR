from mutagen import File, id3
import os
from datetime import datetime
import base64
from typing import Dict, Optional


class MP3File:
    """
    A class representing an MP3 file with its metadata.
    Handles loading and storing MP3 tags and album art.
    """

    def __init__(self, path: str):
        """
        Initialize MP3File object.

        Args:
            path (str): Path to the MP3 file
        """
        self.path = path
        self.tags: Dict[str, str] = {}
        self.original_tags: Dict[str, str] = {}
        self.album_art: Optional[str] = None
        self.load_tags()

    def load_tags(self) -> None:
        """
        Load MP3 tags and album art from the file.
        Stores both original and current tags for comparison.
        """
        try:
            audio = File(self.path)
            if isinstance(audio.tags, id3.ID3):
                self.original_tags = {
                    'title': str(audio.tags.get('TIT2', '')),
                    'artist': str(audio.tags.get('TPE1', '')),
                    'album': str(audio.tags.get('TALB', '')),
                    'filename': os.path.basename(self.path),
                    'modified_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self.tags = self.original_tags.copy()

                # Load album art if exists
                for tag in audio.tags.values():
                    if isinstance(tag, id3.APIC):
                        self.album_art = base64.b64encode(tag.data).decode()
                        break
        except Exception as e:
            print(f"Error loading tags for {self.path}: {str(e)}")

    def has_changes(self) -> bool:
        """
        Check if the file has any changed tags.

        Returns:
            bool: True if any tags have been modified
        """
        return any(
            self.tags.get(key) != self.original_tags.get(key)
            for key in ['title', 'artist', 'album', 'filename']
        )

    def get_display_path(self) -> str:
        """
        Get a user-friendly display path.

        Returns:
            str: Shortened/formatted path for display
        """
        return os.path.basename(self.path)