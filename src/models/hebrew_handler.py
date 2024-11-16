import re
from typing import List, Tuple


class HebrewTextHandler:
    """Handles Hebrew text detection and RTL to LTR conversion"""

    @staticmethod
    def is_hebrew(text: str) -> bool:
        """Check if text contains Hebrew characters"""
        if not text:
            return False
        # הוספת גרש וגרשיים לטווח התווים העבריים
        hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F\u05F3\u05F4]')
        return bool(hebrew_pattern.search(str(text)))

    @staticmethod
    def reverse_hebrew_section(text: str) -> str:
        """
        Creates mirror text for a Hebrew section.
        Preserves geresh (׳) and special characters.
        """
        # Split into words but keep delimiters
        pattern = r'(\s+|[-()\[\]{}])'
        parts = re.split(pattern, text)

        # Process each part
        processed_parts = []
        for part in parts:
            if HebrewTextHandler.is_hebrew(part):
                # Handle geresh specially
                processed = ''
                i = 0
                while i < len(part):
                    if part[i] in '\u05F3\u05F4':  # גרש או גרשיים
                        # שמירת הגרש ליד האות המקורית
                        if processed:
                            processed = processed[:-1] + part[i] + processed[-1]
                        else:
                            processed = part[i]
                    else:
                        processed = part[i] + processed
                    i += 1
                processed_parts.append(processed)
            else:
                processed_parts.append(part)

        # Join all parts and reverse the entire result
        return ''.join(processed_parts[::-1])

    @staticmethod
    def protect_extension(text: str) -> Tuple[str, str]:
        """Separates file extension from text"""
        match = re.search(r'(\.[^. ]+)$', text)
        if match:
            ext = match.group(1)
            return text[:-len(ext)], ext
        return text, ""

    @staticmethod
    def process_text(text: str) -> str:
        """
        Process text by splitting into Hebrew and non-Hebrew sections.

        Args:
            text (str): Input text

        Returns:
            str: Processed text with Hebrew sections mirrored
        """
        # Split by Hebrew/non-Hebrew sections while preserving delimiters
        hebrew_pattern = re.compile(
            r'([\u0590-\u05FF\uFB1D-\uFB4F]+[\u0590-\u05FF\uFB1D-\uFB4F\s()-]*[\u0590-\u05FF\uFB1D-\uFB4F]+|[\u0590-\u05FF\uFB1D-\uFB4F]+)')

        parts = []
        last_end = 0

        for match in hebrew_pattern.finditer(text):
            # Add non-Hebrew text before match
            if match.start() > last_end:
                parts.append((text[last_end:match.start()], False))

            # Add Hebrew text
            parts.append((match.group(), True))
            last_end = match.end()

        # Add remaining non-Hebrew text
        if last_end < len(text):
            parts.append((text[last_end:], False))

        # Process each part
        result = []
        for part, is_hebrew in parts:
            if is_hebrew:
                result.append(HebrewTextHandler.reverse_hebrew_section(part))
            else:
                result.append(part)

        return ''.join(result)

    @staticmethod
    def reverse_hebrew_words(text: str) -> str:
        """
        Create mirror text for Hebrew parts while preserving non-Hebrew text and file extensions.

        Args:
            text (str): Input text

        Returns:
            str: Text with Hebrew sections in mirror form
        """
        if not text:
            return text

        # Protect file extension
        main_text, extension = HebrewTextHandler.protect_extension(text)

        # Process main text
        processed_text = HebrewTextHandler.process_text(main_text)

        # Reattach extension
        return processed_text + extension

    @staticmethod
    def analyze_text(text: str) -> dict:
        """Analyze text for Hebrew content"""
        if not text:
            return {
                'contains_hebrew': False,
                'hebrew_sections': 0,
                'total_sections': 0,
                'needs_conversion': False,
                'original': '',
                'converted': ''
            }

        main_text, extension = HebrewTextHandler.protect_extension(text)
        has_hebrew = HebrewTextHandler.is_hebrew(main_text)
        converted = HebrewTextHandler.reverse_hebrew_words(text) if has_hebrew else text

        return {
            'contains_hebrew': has_hebrew,
            'needs_conversion': has_hebrew,
            'original': text,
            'converted': converted
        }

"""    @staticmethod
    def test_conversion():
       # Test the conversion with various cases
        test_cases = [
            "ששון שאולוב - בואי נדבר.mp3",
            "ששון שאולוב - בואי נדבר (AKI Remix).mp3",
            "שיר ישראלי - test.mp3",
            "Hebrew Song - שיר עברי.mp3",
            "ששון - remix.mp3"
        ]

        print("Testing Hebrew text conversion:")
        print("-" * 50)
        for test in test_cases:
            result = HebrewTextHandler.reverse_hebrew_words(test)
            print(f"Original: {test}")
            print(f"Converted: {result}")
            print("-" * 50)
"""
