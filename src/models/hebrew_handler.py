import re
from typing import List, Tuple


class HebrewTextHandler:
    """Handles Hebrew text detection and RTL to LTR conversion"""

    @staticmethod
    def is_hebrew(text: str) -> bool:
        """
        Check if text contains Hebrew characters.
        More aggressive detection including nikud and special characters.
        """
        if not text:
            return False

        hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]')
        return bool(hebrew_pattern.search(str(text)))

    @staticmethod
    def needs_rtl_fix(text: str) -> bool:
        """
        Check if text contains Hebrew and needs RTL fix.
        More thorough check including context.
        """
        if not text:
            return False

        hebrew_chars = len(re.findall(r'[\u0590-\u05FF\uFB1D-\uFB4F]', text))
        total_chars = len(text.strip())

        return hebrew_chars > 0 and hebrew_chars / total_chars > 0.3

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
        segments = HebrewTextHandler.split_text_to_segments(text)

        # Process each segment
        result = ""
        for segment, is_hebrew in segments:
            if is_hebrew:
                # Reverse only Hebrew segments
                result += segment[::-1]
            else:
                result += segment

        return result

    @staticmethod
    def analyze_text(text: str) -> dict:
        """
        Analyze text for Hebrew content.

        Args:
            text (str): Text to analyze

        Returns:
            dict: Analysis results
        """
        segments = HebrewTextHandler.split_text_to_segments(text)
        hebrew_count = sum(1 for _, is_hebrew in segments if is_hebrew)

        return {
            'contains_hebrew': hebrew_count > 0,
            'hebrew_segments': hebrew_count,
            'total_segments': len(segments),
            'needs_conversion': hebrew_count > 0,
            'original': text,
            'converted': HebrewTextHandler.reverse_hebrew_words(text) if hebrew_count > 0 else text
        }