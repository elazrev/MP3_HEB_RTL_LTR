import os
import io
import mutagen
from mutagen.id3 import ID3, TALB, TIT2, TPE1

SUPPORTED_ENCODINGS = ['utf-8', 'windows-1255']


class MP3File:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.original_tags = self.get_tags()
        self.tags = self.original_tags.copy()
        self.selected = False
        self.album_art = None

    def get_tags(self):
        """Get ID3 tags from the MP3 file"""
        tags = {}
        try:
            audio = ID3(self.path)
            tags = {
                'title': self._get_tag_value(audio.get('TIT2')),
                'artist': self._get_tag_value(audio.get('TPE1')),
                'album': self._get_tag_value(audio.get('TALB'))
            }
        except mutagen.id3.ID3NoHeaderError:
            # File does not have ID3 tags, use filename instead
            tags = {
                'title': os.path.splitext(self.filename)[0],
                'artist': '',
                'album': ''
            }
        except Exception as e:
            print(f"Error getting tags for {self.path}: {str(e)}")

        return tags

    def _get_tag_value(self, tag):
        """Helper function to get tag value, handling different encodings"""
        if tag:
            for encoding in SUPPORTED_ENCODINGS:
                try:
                    return tag.text[0].encode(encoding).decode(encoding)
                except UnicodeDecodeError:
                    continue
        return ''

    def convert_hebrew_tags(self):
        """Convert tags to Hebrew"""
        for key, value in self.tags.items():
            if any(ord(c) >= 0x0590 and ord(c) <= 0x05FF for c in value):
                # Text contains Hebrew characters, convert to Hebrew
                self.tags[key] = self._convert_to_hebrew(value)

    def _convert_to_hebrew(self, text):
        """Convert text to Hebrew"""
        try:
            return text.encode('utf-8').decode('windows-1255')
        except UnicodeDecodeError:
            return text

    def save_changes(self):
        """Save changes to the MP3 file"""
        try:
            audio = ID3(self.path)
            audio['TIT2'] = TIT2(encoding=3, text=self.tags['title'])
            audio['TPE1'] = TPE1(encoding=3, text=self.tags['artist'])
            audio['TALB'] = TALB(encoding=3, text=self.tags['album'])
            audio.save()
            self.original_tags = self.get_tags()
            return True
        except Exception as e:
            print(f"Error saving changes to {self.path}: {str(e)}")
            return False

    def has_changes(self):
        """Check if there are any unsaved changes"""
        return self.tags != self.original_tags

    def get_display_path(self):
        """Get a displayable path for the file"""
        return self.path.split(os.sep)[-2:]