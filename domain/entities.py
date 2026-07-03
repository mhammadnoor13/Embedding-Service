from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

@dataclass(frozen=True)
class EmbeddingRecord:
    consultant_id: UUID
    raw_text: str
    cleaned_text: str
    embedding: List[float]
    
@dataclass(frozen=True)
class SimilarityResult:
    id: UUID
    source: Literal["text", "pdf"] 
    raw_text: str
    pdf_id: Optional[UUID]
    similarity: float
