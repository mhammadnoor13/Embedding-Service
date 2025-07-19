from typing import List
from pydantic import BaseModel


class EmbeddingRecord(BaseModel):
    raw_text: str
    embedding: List[float]
    