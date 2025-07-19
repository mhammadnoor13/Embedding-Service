from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from gotrue import BaseModel
from pydantic import Field
from api.paths import Paths
from application.exceptions import TextCleaningError, TextEmbeddingError
from application.services.similarity_service import SimilarityService
from infrastrcture.embedding.hf_embedding import HFEmbeddingModel
from infrastrcture.supabase_repository.supabase_similarity_repository import SupabaseSimilarityRepository
from infrastrcture.text_cleaner import BasicCleaner

router = APIRouter(tags=["similarity"], prefix="")

class SimilaritySearchIn(BaseModel):
    query: str = Field(..., min_length=1, max_length=5_000)
    k: int = Field(10, ge=1, le=100)
    scope: str = Field("both", pattern="^(text|pdf|both)$")

class SimilarityHit(BaseModel):
    id: UUID
    source: str
    raw_text: str
    pdf_id: Optional[UUID]
    similarity: float

class SimilaritySearchOut(BaseModel):
    results: List[SimilarityHit]

def get_similarity_service() -> SimilarityService:
    cleaner  = BasicCleaner()
    embedder = HFEmbeddingModel()
    repo      = SupabaseSimilarityRepository()
    return SimilarityService(cleaner, embedder, repo)


@router.post(
    Paths.SIMILARITY_SEARCH,
    response_model=SimilaritySearchOut,
    status_code=status.HTTP_200_OK,
)
async def similarity_search(
    payload: SimilaritySearchIn,
    service: SimilarityService = Depends(get_similarity_service),
):
    try:
        hits = await service.execute(payload.query, payload.k, payload.scope)
        return SimilaritySearchOut(
            results=[
                SimilarityHit(
                    id=r.id,
                    source=r.source,
                    raw_text=r.raw_text,
                    pdf_id=r.pdf_id,
                    similarity=r.similarity,
                )
                for r in hits
            ]
        )

    except TextCleaningError as e:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Cleaning error: {e}"
        )
    except TextEmbeddingError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, detail=f"Embedding error: {e}"
        )
    except Exception as e:
        # any other failure (DB, RPC, etc.)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity search failed: {e}"
        )
        