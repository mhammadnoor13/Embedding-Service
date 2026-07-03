import re

from domain.interfaces import ITextCleaner


class BasicCleaner(ITextCleaner):
    def __init__(self):
        self._whitespace_re = re.compile(r"\s+")
        self._control_chars_re = re.compile(r"[\x00-\x1f\x7f-\x9f]")

    def clean(self, text: str) -> str:
        if text is None:
            return ""

        text = self._control_chars_re.sub(" ", text)
        text = self._whitespace_re.sub(" ", text)
        text = text.strip()

        return text