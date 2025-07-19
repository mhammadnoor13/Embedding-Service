import re
from domain.interfaces import ITextCleaner


class BasicCleaner(ITextCleaner):

    def clean(self, text: str) -> str:
        text = text.lower()

        return text