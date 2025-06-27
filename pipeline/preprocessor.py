import re
from typing import Callable, List, Optional

class TextPreprocessor:

    def __init__(self,
                lowercase: bool = False,
                custom_filter: Optional[List[Callable[[str],str]]] = None):
        """
        Args:
            lowercase (bool): If True, run the lowercase filter at the end.
            custom_filters (Optional[List[Callable]]):
                If provided, this list of callables (each taking and returning a string)
                replaces the default filter chain. Otherwise, the default chain is used.
        """

        if custom_filter is not None:
            self._filters: List[Callable[[str],str]] = custom_filter
        else:
            self._filters = [
                self._strip_html,
                self._remove_control_chars,
                self._normalize_punctuation,
                #self._normalize_whitespace,
            ]
            if lowercase:
                self._filters.append(self._lowercase)
    
    def clean(self, text: str) -> str:
        """
        Applies all configured filters in sequence to the input text.

        Args:
            text (str): Raw input string.

        Returns:
            str: Cleaned & normalized text.
        """
        cleaned = text
        for func in self._filters:
            cleaned = func(cleaned)
        return cleaned
    
    def _strip_html(self, text: str) -> str:
        """
        Removes any HTML tags using a simple regex.
        NOTE: This is not a full HTML parser. It strips patterns like <...>.
        """

        script_pattern = re.compile(r"<(script|style).*?>.*?</\1>", flags=re.DOTALL | re.IGNORECASE)
        text = script_pattern.sub(" ", text)

        tag_pattern = re.compile(r"<[^>]+>")
        return tag_pattern.sub(" ", text)
    
    def _remove_control_chars(self, text: str) -> str:
        """
        Strips out non-printable control characters (Unicode category Cc)
        and replaces them with a space. This also removes zero-width spaces, etc.
        """
        # Unicode category 'C' includes control characters; regex \p{C} needs the regex module,
        # but Python's 're' does not support \p{...}. Instead, we remove characters in ranges
        # U+0000–U+001F and U+007F–U+009F, as well as other known zero-width codepoints.
        control_chars = [
            (0x0000, 0x001F),
            (0x007F, 0x009F),
            (0x200B, 0x200F),  # zero-width and bidi controls
            (0x202A, 0x202E)   # more bidi controls
        ]

        # Build a regex character class for those ranges
        ranges = []
        for start, end in control_chars:
            # Convert to Python regex range syntax
            ranges.append(f"\\u{start:04X}-\\u{end:04X}")
        char_class = "[" + "".join(ranges) + "]"

        pattern = re.compile(char_class)
        return pattern.sub(" ", text)
    
    def _normalize_punctuation(self, text: str) -> str:
        """
        Normalizes common “fancy” punctuation to ASCII equivalents:
          - Converts curly quotes to straight quotes
          - Converts long dashes (—, –) to hyphens (-)
          - Converts ellipsis (…) to three dots (...)
        """
        # Map of fancy→plain
        replacements = {
            "\u2018": "'",  # left single quote
            "\u2019": "'",  # right single quote / apostrophe
            "\u201C": '"',  # left double quote
            "\u201D": '"',  # right double quote
            "\u2013": "-",  # en dash
            "\u2014": "-",  # em dash
            "\u2026": "...",  # ellipsis
            "\u00A0": " ",   # non-breaking space → normal space
        }
        # Use regex to replace all occurrences
        def repl(match):
            char = match.group(0)
            return replacements.get(char, char)

        # Build a character‐class pattern matching any key in replacements
        chars = "".join(re.escape(key) for key in replacements.keys())
        pattern = re.compile(f"[{chars}]")
        return pattern.sub(repl, text)
    
    def _lowercase(self, text: str) -> str:
        """
        Converts all characters to lowercase. Run this last if requested.
        """
        return text.lower()
