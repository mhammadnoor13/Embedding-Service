from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities import SimilarityResult


class ITextCleaner(ABC):
    @abstractmethod
    def clean(self, text: str) -> str: ...

class IEmbeddingModel(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]: ...

class ITextRepository(ABC):
    async def add(self, text: str, embedding: List[float]) -> str: ...

class IPDFChunker(ABC):
    def chunk(self, pdf_bytes: bytes) -> List[str]: ...

class IPDFRepository(ABC):
    async def create_pdf(self, filename: str, consultant_id: UUID) -> UUID:
        ''' Insert a row in "pdf_file" with status "Pending", return its UUID.'''
        ...

    async def add_chunk(
        self,
        pdf_id: UUID,
        chunk_index: int,
        raw_text: str,
        embedding: List[float],
    ) -> UUID:
        ''' Insert one chunk into "pdf_chunks", return its UUID.'''
        ...
    
    async def update_status(self, pdf_id: UUID, status: str) -> None:
        ''' Changing status of the pdf '''

class ISimilarityRepository(ABC):
    async def search(
        self,
        embedding: List[float],
        k: int,
        scope: str #text | pdf | both
    ) -> List[SimilarityResult]:
        ...