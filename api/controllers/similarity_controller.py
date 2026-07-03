from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status as http_status
from pydantic import BaseModel, Field

from api.dependencies import get_similarity_service
from api.paths import Paths
from application.exceptions import TextCleaningError, TextEmbeddingError
from application.services.similarity_service import SimilarityService


router = APIRouter(tags=["similarity"])


class SimilaritySearchIn(BaseModel):
    query: str = Field(..., min_length=1, max_length=5_000)
    k: int = Field(10, ge=1, le=50)
    scope: str = Field("both", pattern="^(text|pdf|both)$")
    min_similarity: float = Field(0.70, ge=0.0, le=1.0)


class SimilarityHit(BaseModel):
    id: UUID
    source: str
    raw_text: str
    pdf_id: Optional[UUID]
    similarity: float


class SimilaritySearchOut(BaseModel):
    results: List[SimilarityHit]


@router.post(
    Paths.SIMILARITY_SEARCH,
    response_model=SimilaritySearchOut,
    status_code=http_status.HTTP_200_OK,
)
async def similarity_search(
    payload: SimilaritySearchIn,
    x_user_id: Optional[UUID] = Header(None, alias="X-User-Id"),
    service: SimilarityService = Depends(get_similarity_service),
):
    if x_user_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    try:
        hits = await service.execute(
            consultant_id=x_user_id,
            query=payload.query,
            k=payload.k,
            scope=payload.scope,
            min_similarity=payload.min_similarity,
        )

        return SimilaritySearchOut(
            results=[
                SimilarityHit(
                    id=result.id,
                    source=result.source,
                    raw_text=result.raw_text,
                    pdf_id=result.pdf_id,
                    similarity=result.similarity,
                )
                for result in hits
            ]
        )

    except TextCleaningError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except TextEmbeddingError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similarity search failed: {exc}",
        )