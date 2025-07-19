from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class EmbeddingRecord(BaseModel):
    raw_text: str
    embedding: List[float]
    
class SimilarityResult(BaseModel):
    id: UUID
    source: str  # 'text' or 'pdf'
    raw_text: str
    pdf_id: Optional[UUID]
    similarity: float
