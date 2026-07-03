from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    UploadFile,
    status as http_status,
)
from pydantic import BaseModel

from api.dependencies import get_embed_pdf_service, get_pdf_status_service
from api.paths import Paths
from application.exceptions import (
    PdfChunkingError,
    PdfCleaningError,
    PdfEmbeddingError,
    PdfNotFoundError,
    PdfPersistenceError,
    PdfProcessingError,
)
from application.services.embed_pdf_service import EmbedPdfService
from application.services.pdf_status_service import PdfStatusService


router = APIRouter(tags=["embedding"])


class PdfUploadOut(BaseModel):
    pdf_id: UUID


class PdfStatusOut(BaseModel):
    status: str


@router.post(
    Paths.EMBED_PDF,
    response_model=PdfUploadOut,
    status_code=http_status.HTTP_202_ACCEPTED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    x_user_id: Optional[UUID] = Header(None, alias="X-User-Id"),
    service: EmbedPdfService = Depends(get_embed_pdf_service),
):
    if x_user_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=http_status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only application/pdf is supported",
        )

    body = await file.read()

    if not body:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF is empty",
        )

    filename = file.filename or "uploaded.pdf"

    try:
        pdf_id = await service.execute(body, x_user_id, filename=filename)
        return PdfUploadOut(pdf_id=pdf_id)

    except (PdfChunkingError, PdfCleaningError) as exc:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except PdfEmbeddingError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except PdfPersistenceError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    except PdfProcessingError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )


@router.get(
    Paths.EMBED_PDF_STATUS,
    response_model=PdfStatusOut,
    status_code=http_status.HTTP_200_OK,
)
async def get_pdf_status(
    pdf_id: UUID,
    service: PdfStatusService = Depends(get_pdf_status_service),
):
    try:
        status = await service.execute(pdf_id)
        return PdfStatusOut(status=status)

    except PdfNotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )

    except PdfPersistenceError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )