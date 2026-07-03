import io
import re
from typing import List

from pypdf import PdfReader

from domain.interfaces import IPDFChunker


class PdfChunker(IPDFChunker):
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap
        self._whitespace_re = re.compile(r"\s+")

    def chunk(self, pdf_bytes: bytes) -> List[str]:
        reader = PdfReader(io.BytesIO(pdf_bytes))

        page_texts: List[str] = []

        for page in reader.pages:
            text = page.extract_text() or ""
            text = self._whitespace_re.sub(" ", text).strip()

            if text:
                page_texts.append(text)

        full_text = " ".join(page_texts).strip()

        if not full_text:
            return []

        words = full_text.split()
        chunks: List[str] = []

        step = self.chunk_size - self.overlap

        for start in range(0, len(words), step):
            end = start + self.chunk_size
            chunk = " ".join(words[start:end]).strip()

            if chunk:
                chunks.append(chunk)

        return chunks