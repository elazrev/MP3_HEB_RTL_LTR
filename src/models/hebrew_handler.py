import re
from typing import List, Tuple


class HebrewTextHandler:
    """Handles Hebrew text detection and RTL to LTR conversion"""

    @staticmethod
    def is_hebrew(text: str) -> bool:
        """
        Check if text contains Hebrew characters.

        Args:
            text (str): Text to check

        Returns:
            bool: True if text contains Hebrew characters
        """
        if not text:
            return False
        # הרחבת הטווח לכל התווים העבריים כולל ניקוד
        hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]')
        return bool(hebrew_pattern.search(str(text)))

    @staticmethod
    def split_text_to_segments(text: str) -> List[Tuple[str, bool]]:
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
        # עדכון הטווח גם כאן
        hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]+')

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
            str: Text with Hebrew segments reversed while keeping word structure
        """
        if not text:
            return text

        # Split into words but preserve spaces and punctuation
        pattern = r'([^\s\W]+|\s+|[^\w\s])'
        parts = re.findall(pattern, text)

        result = []
        for part in parts:
            if HebrewTextHandler.is_hebrew(part):
                # Reverse only if it's a Hebrew word
                result.append(part[::-1])
            else:
                # Keep non-Hebrew parts as is
                result.append(part)

        return ''.join(result)

    @staticmethod
    def analyze_text(text: str) -> dict:
        """
        Analyze text for Hebrew content.

        Args:
            text (str): Text to analyze

        Returns:
            dict: Analysis results including:
                - contains_hebrew: bool
                - hebrew_segments: int
                - total_segments: int
                - needs_conversion: bool
                - original: str
                - converted: str
        """
        if not text:
            return {
                'contains_hebrew': False,
                'hebrew_segments': 0,
                'total_segments': 0,
                'needs_conversion': False,
                'original': '',
                'converted': ''
            }

        # Analyze using split_text_to_segments
        segments = HebrewTextHandler.split_text_to_segments(text)
        hebrew_count = sum(1 for _, is_hebrew in segments if is_hebrew)

        # Only convert if Hebrew is detected
        needs_conversion = hebrew_count > 0
        converted = HebrewTextHandler.reverse_hebrew_words(text) if needs_conversion else text

        return {
            'contains_hebrew': hebrew_count > 0,
            'hebrew_segments': hebrew_count,
            'total_segments': len(segments),
            'needs_conversion': needs_conversion,
            'original': text,
            'converted': converted
        }