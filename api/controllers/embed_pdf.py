from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from api.paths import Paths
from application.exceptions import PdfChunkingError, PdfEmbeddingError, PdfPersistenceError
from application.services.embed_pdf_service import EmbedPdfService
from infrastrcture.chunking.pdf_chunker import PdfChunker
from infrastrcture.embedding.hf_embedding import HFEmbeddingModel
from infrastrcture.supabase_repository.supabase_pdf_repository import SupabasePdfRepository
from infrastrcture.text_cleaner import BasicCleaner


router = APIRouter(tags=["embedding"], prefix="")

class PdfUploadOut(BaseModel):
    pdf_id: UUID

class PdfStatusOut(BaseModel):
    status: str  

def get_embed_pdf_service() -> EmbedPdfService:

    return EmbedPdfService(
        chunker=PdfChunker(chunk_size=1000, overlap=200),
        cleaner=BasicCleaner(),
        embedder=HFEmbeddingModel(),
        repo=SupabasePdfRepository(),
    )

@router.post(
    Paths.EMBED_PDF,
    response_model=PdfUploadOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    service: EmbedPdfService = Depends(get_embed_pdf_service),
):
    """
    Accept a PDF file, enqueue/process its chunks, and return a pdf_id.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only application/pdf is supported",
        )

    body = await file.read()
    try:
        pdf_id = await service.execute(body, filename=file.filename)
    except (PdfChunkingError, PdfEmbeddingError, PdfPersistenceError) as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF processing failed: {e}",
        )
    return PdfUploadOut(pdf_id=pdf_id)  


@router.get(
    Paths.EMBED_PDF_STATUS,
    response_model=PdfStatusOut,
)
async def get_pdf_status(
    pdf_id: UUID,
    service = Depends(get_embed_pdf_service), 
):
    repo = service.repo
    """
    Return the current status of the PDF processing.
    """
    try:
        row = await repo.client.table("pdf_files").select("status")\
                           .eq("id", str(pdf_id)).single().execute()
        data = row.data or {}
        status_val = data.get("status")
        if status_val is None:
            raise KeyError
        return PdfStatusOut(status=status_val)
    except KeyError:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="PDF not found",
        )
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch PDF status",
        )