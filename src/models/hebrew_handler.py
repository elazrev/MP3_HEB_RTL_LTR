import re
from typing import List, Tuple


class HebrewTextHandler:
    """Handles Hebrew text detection and RTL to LTR conversion"""

    HEBREW_CHARS_RANGE = (
        r'[\u0590-\u05FF'  # Hebrew chars
        r'\uFB1D-\uFB4F'  # Hebrew presentation forms
        r'\u05D0-\u05EA'  # Basic Hebrew letters
        r'\u05F0-\u05F4'  # Hebrew ligatures and punctuation
        r']'
    )

    @staticmethod
    def is_hebrew(text: str) -> bool:
        """Check if text contains Hebrew characters"""
        if not text or not isinstance(text, str):
            return False
        hebrew_pattern = re.compile(HebrewTextHandler.HEBREW_CHARS_RANGE)
        return bool(hebrew_pattern.search(text))

    @staticmethod
    def split_text_to_segments(text: str) -> List[Tuple[str, bool]]:
        """Split text into Hebrew and non-Hebrew segments"""
        if not text or not isinstance(text, str):
            return []

        # Split text into words
        words = text.split()
        segments = []

        for word in words:
            # Check if word contains Hebrew
            has_hebrew = bool(re.search(HebrewTextHandler.HEBREW_CHARS_RANGE, word))
            segments.append((word, has_hebrew))
            # Add space after each word except the last one
            if word != words[-1]:
                segments.append((" ", False))

        return segments

    @staticmethod
    def reverse_hebrew_words(text: str) -> str:
        """Reverse Hebrew words while preserving word order"""
        if not text or not isinstance(text, str):
            return text

        # Split into segments
        segments = HebrewTextHandler.split_text_to_segments(text)

        # Process each segment
        result = ""
        for segment, is_hebrew in segments:
            if is_hebrew:
                # Reverse only the Hebrew segments
                result += segment[::-1]
            else:
                result += segment

        return result