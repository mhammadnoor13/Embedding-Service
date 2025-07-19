from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from application.exceptions import TextEmbeddingError, TextPersistenceError
from application.services.embed_text import EmbedTextService
from infrastrcture.embedding.hf_embedding import HFEmbeddingModel
from infrastrcture.supabase_repository.supabase_text_repository import SupaBaseTextRepository
from infrastrcture.text_cleaner import BasicCleaner
from api.paths import Paths


router = APIRouter(tags=["embedding"])

class EmbedTextIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_00)

class EmbedTextOut(BaseModel):
    id: UUID


def get_embed_text_service() -> EmbedTextService:
    cleaner  = BasicCleaner()
    embedder = HFEmbeddingModel()
    repo     = SupaBaseTextRepository()
    return EmbedTextService(cleaner, embedder, repo)

@router.post(
    Paths.EMBED_TEXT,
    response_model=EmbedTextOut,
)
async def embed_text(
    payload: EmbedTextIn,
    service: EmbedTextService = Depends(get_embed_text_service),
):
    try:
        new_id = await service.execute(payload.text)
        return EmbedTextOut(id= new_id)
    except TextEmbeddingError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding provider error: {e}"
        )
    except TextPersistenceError as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Persistence error: {e}"
        )