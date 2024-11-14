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
        self.selected = False


    def save_changes(self) -> bool:
        """Save changes to the file"""
        try:
            if not self.has_changes():
                return True

            print(f"Saving changes to {self.path}")  # Debug print
            print(f"Original tags: {self.original_tags}")  # Debug print
            print(f"New tags: {self.tags}")  # Debug print

            # Create backup first
            backup_path = f"{self.path}.bak"
            shutil.copy2(self.path, backup_path)

            try:
                # Load audio file
                audio = File(self.path)
                if not isinstance(audio.tags, id3.ID3):
                    audio.add_tags()

                # Update each tag
                if self.tags['title'] != self.original_tags['title']:
                    audio.tags['TIT2'] = id3.TIT2(encoding=3, text=[self.tags['title']])
                    print(f"Updated title to: {self.tags['title']}")  # Debug print

                if self.tags['artist'] != self.original_tags['artist']:
                    audio.tags['TPE1'] = id3.TPE1(encoding=3, text=[self.tags['artist']])
                    print(f"Updated artist to: {self.tags['artist']}")  # Debug print

                if self.tags['album'] != self.original_tags['album']:
                    audio.tags['TALB'] = id3.TALB(encoding=3, text=[self.tags['album']])
                    print(f"Updated album to: {self.tags['album']}")  # Debug print

                # Save the tags
                audio.save()

                # Handle filename change
                if self.tags['filename'] != self.original_tags['filename']:
                    new_path = os.path.join(os.path.dirname(self.path), self.tags['filename'])
                    print(f"Renaming file to: {new_path}")  # Debug print

                    # Make sure we don't overwrite existing files
                    if os.path.exists(new_path):
                        base_name, ext = os.path.splitext(new_path)
                        counter = 1
                        while os.path.exists(f"{base_name}_{counter}{ext}"):
                            counter += 1
                        new_path = f"{base_name}_{counter}{ext}"

                    os.rename(self.path, new_path)
                    self.path = new_path

                # Update original tags to reflect changes
                self.original_tags = self.tags.copy()

                # Remove backup after successful save
                os.remove(backup_path)
                return True

            except Exception as e:
                print(f"Error during save: {str(e)}")  # Debug print
                # Restore from backup if something went wrong
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, self.path)
                    os.remove(backup_path)
                raise e

        except Exception as e:
            print(f"Error saving changes: {str(e)}")  # Debug print
            return False

    def convert_hebrew_tags(self) -> None:
        """Convert Hebrew text in all tags"""
        from .hebrew_handler import HebrewTextHandler

        print(f"Converting tags for: {self.path}")  # Debug print
        print(f"Original tags: {self.tags}")  # Debug print

        for tag_name in ['title', 'artist', 'album', 'filename']:
            if HebrewTextHandler.is_hebrew(self.tags[tag_name]):
                self.tags[tag_name] = HebrewTextHandler.reverse_hebrew_words(
                    self.tags[tag_name]
                )
                print(f"Converted {tag_name}: {self.tags[tag_name]}")  # Debug print

    def has_changes(self) -> bool:
        """Check if there are any changes in tags"""
        return any(
            self.tags.get(key) != self.original_tags.get(key)
            for key in self.tags.keys()
        )

    def get_display_path(self) -> str:
        """Get display path"""
        return os.path.basename(self.path)