from mutagen import File, id3
import os
from typing import Dict, Optional, List
import base64
from .hebrew_handler import HebrewTextHandler


class MP3File:
    """Represents an MP3 file with its metadata"""

    def __init__(self, path: str):
        self.path = path
        self.tags: Dict[str, str] = {}
        self.original_tags: Dict[str, str] = {}
        self.album_art: Optional[str] = None
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
                        self.album_art = base64.b64encode(tag.data).decode()
                        break
        except Exception as e:
            print(f"Error loading tags from {self.path}: {str(e)}")
            # Set default values if loading fails
            self.original_tags = {
                'title': os.path.basename(self.path),
                'artist': '',
                'album': '',
                'filename': os.path.basename(self.path)
            }
            self.tags = self.original_tags.copy()

    def analyze_tags(self) -> None:
        """Analyze tags for Hebrew content"""
        for tag_name, tag_value in self.original_tags.items():
            self.hebrew_analysis[tag_name] = HebrewTextHandler.analyze_text(tag_value)

    def has_hebrew(self) -> bool:
        """Check if any tag contains Hebrew text"""
        return any(
            analysis['contains_hebrew']
            for analysis in self.hebrew_analysis.values()
        )

    def convert_hebrew_tags(self) -> None:
        """Convert Hebrew text in tags from RTL to LTR"""
        for tag_name, analysis in self.hebrew_analysis.items():
            if analysis['needs_conversion']:
                self.tags[tag_name] = analysis['converted']

    def has_changes(self) -> bool:
        """Check if there are any changes in tags"""
        return any(
            self.tags.get(key) != self.original_tags.get(key)
            for key in self.tags.keys()
        )

    def get_display_path(self) -> str:
        """Get a user-friendly display path"""
        return os.path.basename(self.path)

    def get_tag_preview(self, tag_name: str) -> Dict:
        """
        Get preview of original and converted tag value

        Args:
            tag_name (str): Name of the tag

        Returns:
            Dict: Original and converted values with Hebrew analysis
        """
        return {
            'original': self.original_tags.get(tag_name, ''),
            'converted': self.tags.get(tag_name, ''),
            'analysis': self.hebrew_analysis.get(tag_name, {})
        }

    def __str__(self) -> str:
        return f"{self.tags.get('artist', '')} - {self.tags.get('title', '')}"