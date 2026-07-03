from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities import EmbeddingRecord, SimilarityResult


class ITextCleaner(ABC):
    @abstractmethod
    def clean(self, text: str) -> str: 
        pass

class IEmbeddingModel(ABC):
    @abstractmethod
    async def embed(self, text: str) -> List[float]: 
        pass

class ITextRepository(ABC):
    @abstractmethod
    async def add(self, record: EmbeddingRecord) -> UUID: 
        pass

class IPDFChunker(ABC):
    @abstractmethod
    def chunk(self, pdf_bytes: bytes) -> List[str]: 
        pass

class IPDFRepository(ABC):
    async def create_pdf(self, filename: str, consultant_id: UUID) -> UUID:

        ''' Insert a row in "pdf_file" with status "Pending", return its UUID.'''
        pass

    @abstractmethod
    async def add_chunk(
        self,
        pdf_id: UUID,
        chunk_index: int,
        raw_text: str,
        cleaned_text: str,
        embedding: List[float],
    ) -> UUID:
        ''' Insert one chunk into "pdf_chunks", return its UUID.'''
        ...
    
    @abstractmethod
    async def update_status(self, pdf_id: UUID, status: str) -> None:
        ''' Changing status of the pdf '''

    @abstractmethod
    async def get_status(self, pdf_id: UUID) -> Optional[str]:
        """
        Return the processing status of a PDF, or None if the PDF does not exist.
        """
        pass

class ISimilarityRepository(ABC):
    @abstractmethod
    async def search(
        self,
        consultant_id: UUID,
        embedding: List[float],
        k: int,
        scope: str, #text | pdf | both
        min_similarity: float,
    ) -> List[SimilarityResult]:
        pass