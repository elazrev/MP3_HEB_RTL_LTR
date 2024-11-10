import re
import os
from typing import Dict, List, Optional
from datetime import datetime
from .mp3_file import MP3File


class HebrewFixer:
    """Core logic for handling Hebrew text in MP3 files"""

    def __init__(self):
        """Initialize the HebrewFixer with empty collections"""
        self.files_to_process: Dict[str, MP3File] = {}
        self.history: List[Dict] = []
        self.current_directory: Optional[str] = None

    @staticmethod
    def is_hebrew(text: str) -> bool:
        """Check if text contains Hebrew characters"""
        if not text:
            return False
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        return bool(hebrew_pattern.search(str(text)))

    @staticmethod
    def split_text_to_segments(text: str) -> List[tuple[str, bool]]:
        """
        Split text into segments of Hebrew and non-Hebrew text.

        Args:
            text (str): Input text containing mixed Hebrew and non-Hebrew

        Returns:
            List[Tuple[str, bool]]: List of (text_segment, is_hebrew) tuples
        """
        if not text:
            return []

        segments = []
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]+')

        # Find all Hebrew segments with their positions
        matches = list(hebrew_pattern.finditer(text))

        if not matches:
            return [(text, False)]

        last_end = 0
        for match in matches:
            start, end = match.span()

            # Add non-Hebrew segment before match if exists
            if start > last_end:
                segments.append((text[last_end:start], False))

            # Add Hebrew segment
            segments.append((text[start:end], True))
            last_end = end

        # Add remaining non-Hebrew segment if exists
        if last_end < len(text):
            segments.append((text[last_end:], False))

        return segments

    @staticmethod
    def reverse_hebrew_words(text: str) -> str:
        """
        Reverse Hebrew text while preserving word structure and non-Hebrew text.

        Args:
            text (str): Text containing Hebrew and possibly non-Hebrew characters

        Returns:
            str: Text with Hebrew segments reversed
        """
        if not text:
            return text

        # Split into segments
        segments = HebrewFixer.split_text_to_segments(text)

        # Process each segment
        result = ""
        for segment, is_hebrew in segments:
            if is_hebrew:
                # Reverse only Hebrew segments
                result += segment[::-1]
            else:
                result += segment

        return result

    def process_file(self, file_path: str) -> MP3File:
        """Process a single MP3 file"""
        mp3_file = MP3File(file_path)

        # Process all relevant tags
        for tag in ['title', 'artist', 'album', 'filename']:
            if self.is_hebrew(mp3_file.tags[tag]):
                mp3_file.tags[tag] = self.reverse_hebrew_words(mp3_file.tags[tag])

        return mp3_file

    def scan_directory(self, directory: str) -> List[MP3File]:
        """Scan directory for MP3 files"""
        self.current_directory = directory
        found_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.mp3'):
                    file_path = os.path.join(root, file)
                    mp3_file = self.process_file(file_path)
                    found_files.append(mp3_file)

        return found_files

    def save_changes(self, file: MP3File) -> bool:
        """Save changes to file and add to history"""
        try:
            # Implement actual file saving logic here
            # For now, just add to history
            self.add_to_history(file)
            return True
        except Exception as e:
            print(f"Error saving changes: {str(e)}")
            return False

    def add_to_history(self, file: MP3File) -> None:
        """Add file operation to history"""
        self.history.append({
            'path': file.path,
            'original_tags': file.original_tags.copy(),
            'new_tags': file.tags.copy(),
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def undo_last_change(self) -> bool:
        """Undo the last change from history"""
        if not self.history:
            return False

        last_change = self.history.pop()
        try:
            file = MP3File(last_change['path'])
            file.tags = last_change['original_tags']
            return self.save_changes(file)
        except Exception as e:
            print(f"Error undoing changes: {str(e)}")
            return False

    def clear(self) -> None:
        """Clear all processed files and reset state"""
        self.files_to_process.clear()
        self.current_directory = None