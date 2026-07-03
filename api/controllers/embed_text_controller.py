from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status as http_status
from pydantic import BaseModel, Field

from api.dependencies import get_embed_text_service
from api.paths import Paths
from application.exceptions import (
    TextCleaningError,
    TextEmbeddingError,
    TextPersistenceError,
)
from application.services.embed_text import EmbedTextService


router = APIRouter(tags=["embedding"])


class EmbedTextIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)


class EmbedTextOut(BaseModel):
    id: UUID


@router.post(
    Paths.EMBED_TEXT,
    response_model=EmbedTextOut,
    status_code=http_status.HTTP_201_CREATED,
)
async def embed_text(
    payload: EmbedTextIn,
    x_user_id: Optional[UUID] = Header(None, alias="X-User-Id"),
    service: EmbedTextService = Depends(get_embed_text_service),
):
    if x_user_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    try:
        new_id = await service.execute(payload.text, x_user_id)
        return EmbedTextOut(id=new_id)

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

    except TextPersistenceError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )