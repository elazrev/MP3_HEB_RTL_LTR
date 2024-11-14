from mutagen import File, id3
import os
from typing import Dict, Optional
import base64
import shutil
from .hebrew_handler import HebrewTextHandler


class MP3File:
    """
    A class representing an MP3 file with its metadata.
    Handles loading, modifying, and saving MP3 tags and album art.
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
        self.selected: bool = False
        self.hebrew_analysis: Dict[str, Dict] = {}
        self.load_tags()
        self.analyze_tags()

    def load_tags(self) -> None:
        """Load MP3 tags and album art from file"""
        try:
            audio = File(self.path)
            if isinstance(audio.tags, id3.ID3):
                self.original_tags = {
                    'title': str(audio.tags.get('TIT2', '')),
                    'artist': str(audio.tags.get('TPE1', '')),
                    'album': str(audio.tags.get('TALB', '')),
                    'filename': os.path.basename(self.path)
                }
                self.tags = self.original_tags.copy()

                # Load album art if exists
                for tag in audio.tags.values():
                    if isinstance(tag, id3.APIC):
                        try:
                            self.album_art = base64.b64encode(tag.data).decode()
                            break
                        except Exception as e:
                            print(f"Error loading album art: {str(e)}")
                            continue

        except Exception as e:
            print(f"Error loading tags from {self.path}: {str(e)}")
            # Set default values if loading fails
            filename = os.path.basename(self.path)
            self.original_tags = {
                'title': filename,
                'artist': '',
                'album': '',
                'filename': filename
            }
            self.tags = self.original_tags.copy()

    def analyze_tags(self) -> None:
        """Analyze tags for Hebrew content"""
        for tag_name, tag_value in self.original_tags.items():
            self.hebrew_analysis[tag_name] = HebrewTextHandler.analyze_text(tag_value)

    def has_hebrew(self) -> bool:
        """
        Check if any tag contains Hebrew text.

        Returns:
            bool: True if any tag contains Hebrew text
        """
        return any(
            analysis['contains_hebrew']
            for analysis in self.hebrew_analysis.values()
        )

    def has_changes(self) -> bool:
        """
        Check if there are any changes in tags.

        Returns:
            bool: True if any tag has been modified
        """
        return any(
            self.tags.get(key) != self.original_tags.get(key)
            for key in ['title', 'artist', 'album', 'filename']
        )

    def convert_hebrew_tags(self) -> None:
        """Convert Hebrew text in all tags from RTL to LTR"""
        for tag_name, analysis in self.hebrew_analysis.items():
            if analysis['needs_conversion']:
                self.tags[tag_name] = analysis['converted']

    def save_changes(self) -> bool:
        """
        Save changes to the file.

        Returns:
            bool: True if save was successful
        """
        if not self.has_changes():
            return True

        # Create backup
        backup_path = f"{self.path}.bak"
        try:
            shutil.copy2(self.path, backup_path)
        except Exception as e:
            print(f"Failed to create backup: {str(e)}")
            return False

        try:
            # Load and modify tags
            audio = File(self.path)
            if not isinstance(audio.tags, id3.ID3):
                audio.add_tags()

            # Update each tag if changed
            if self.tags['title'] != self.original_tags['title']:
                audio.tags['TIT2'] = id3.TIT2(encoding=3, text=[self.tags['title']])

            if self.tags['artist'] != self.original_tags['artist']:
                audio.tags['TPE1'] = id3.TPE1(encoding=3, text=[self.tags['artist']])

            if self.tags['album'] != self.original_tags['album']:
                audio.tags['TALB'] = id3.TALB(encoding=3, text=[self.tags['album']])

            # Save tag changes
            audio.save()

            # Handle filename change
            if self.tags['filename'] != self.original_tags['filename']:
                new_path = os.path.join(os.path.dirname(self.path), self.tags['filename'])

                # Ensure unique filename
                if os.path.exists(new_path):
                    base, ext = os.path.splitext(new_path)
                    counter = 1
                    while os.path.exists(f"{base}_{counter}{ext}"):
                        counter += 1
                    new_path = f"{base}_{counter}{ext}"

                # Rename file
                os.rename(self.path, new_path)
                self.path = new_path

            # Update original tags to reflect changes
            self.original_tags = self.tags.copy()

            # Remove backup after successful save
            os.remove(backup_path)
            return True

        except Exception as e:
            print(f"Error saving changes to {self.path}: {str(e)}")
            # Restore from backup if something went wrong
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, self.path)
                except Exception as restore_error:
                    print(f"Error restoring from backup: {str(restore_error)}")
                finally:
                    try:
                        os.remove(backup_path)
                    except:
                        pass
            return False

    def get_display_path(self) -> str:
        """
        Get a user-friendly display path.

        Returns:
            str: Shortened/formatted path for display
        """
        return os.path.basename(self.path)

    def get_tag_preview(self, tag_name: str) -> Dict:
        """
        Get preview of original and converted tag value.

        Args:
            tag_name (str): Name of the tag to preview

        Returns:
            Dict: Original and converted values with Hebrew analysis
        """
        return {
            'original': self.original_tags.get(tag_name, ''),
            'converted': self.tags.get(tag_name, ''),
            'analysis': self.hebrew_analysis.get(tag_name, {})
        }

    def __str__(self) -> str:
        """String representation of the file"""
        return f"{self.tags.get('artist', '')} - {self.tags.get('title', '')}"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"MP3File(path='{self.path}', has_hebrew={self.has_hebrew()}, has_changes={self.has_changes()})"