from mutagen import File, id3
import os
from typing import Dict, Optional
import base64
import shutil


class MP3File:
    def __init__(self, path: str):
        self.path = path
        self.tags: Dict[str, str] = {}
        self.original_tags: Dict[str, str] = {}
        self.album_art: Optional[str] = None
        self.selected = False  # Added selected flag
        self.load_tags()

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

                # Load album art
                for tag in audio.tags.values():
                    if isinstance(tag, id3.APIC):
                        try:
                            self.album_art = base64.b64encode(tag.data).decode()
                            break
                        except:
                            pass

        except Exception as e:
            print(f"Error loading tags from {self.path}: {str(e)}")
            self.original_tags = {
                'title': os.path.basename(self.path),
                'artist': '',
                'album': '',
                'filename': os.path.basename(self.path)
            }
            self.tags = self.original_tags.copy()

    def save_changes(self) -> bool:
        """Save changes to the file"""
        try:
            if not self.has_changes():
                return True

            # Create backup
            backup_path = f"{self.path}.bak"
            shutil.copy2(self.path, backup_path)

            try:
                # Load and modify tags
                audio = File(self.path)
                if not isinstance(audio.tags, id3.ID3):
                    audio.add_tags()

                # Update tags
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
                    if os.path.exists(new_path):
                        base, ext = os.path.splitext(new_path)
                        counter = 1
                        while os.path.exists(f"{base}_{counter}{ext}"):
                            counter += 1
                        new_path = f"{base}_{counter}{ext}"

                    os.rename(self.path, new_path)
                    self.path = new_path

                # Remove backup after successful save
                os.remove(backup_path)

                # Update original tags
                self.original_tags = self.tags.copy()
                return True

            except Exception as e:
                # Restore from backup if something went wrong
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, self.path)
                    os.remove(backup_path)
                raise e

        except Exception as e:
            print(f"Error saving changes to {self.path}: {str(e)}")
            return False