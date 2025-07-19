import io
import re
from typing import List

from pypdf import PdfReader
from domain.interfaces import IPDFChunker


class PdfChunker(IPDFChunker):
    def __init__(self, chunk_size: int = 200, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._ws_re = re.compile(r"\s+")

    def chunk(self, pdf_bytes) -> list[str]:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_texts: List[str] = []
        for pages in reader.pages:
            text = pages.extract_text() or ""
            text = self._ws_re.sub(" ", text).strip()
            if text:
                page_texts.append(text)
        full_text = " ".join(page_texts)

        chunks = []
        start = 0
        words = full_text.split()
        total = len(words)
        step = self.chunk_size - self.overlap
        for start in range(0, total, step):
            end = start + self.chunk_size
            chunks.append(" ".join(words[start:end]))
        return chunks
            