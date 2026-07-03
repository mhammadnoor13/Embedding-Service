from functools import lru_cache

from application.services.embed_pdf_service import EmbedPdfService
from application.services.embed_text import EmbedTextService
from application.services.pdf_status_service import PdfStatusService
from application.services.similarity_service import SimilarityService

from infrastructure.chunking.pdf_chunker import PdfChunker
from infrastructure.embedding.hf_embedding import HFEmbeddingModel
from infrastructure.supabase_repository.supabase_pdf_repository import SupabasePdfRepository
from infrastructure.supabase_repository.supabase_similarity_repository import SupabaseSimilarityRepository
from infrastructure.supabase_repository.supabase_text_repository import SupabaseTextRepository
from infrastructure.text_cleaner import BasicCleaner


@lru_cache
def get_cleaner() -> BasicCleaner:
    return BasicCleaner()


@lru_cache
def get_embedding_model() -> HFEmbeddingModel:
    return HFEmbeddingModel()


@lru_cache
def get_pdf_chunker() -> PdfChunker:
    return PdfChunker(chunk_size=1000, overlap=200)


@lru_cache
def get_text_repository() -> SupabaseTextRepository:
    return SupabaseTextRepository()


@lru_cache
def get_pdf_repository() -> SupabasePdfRepository:
    return SupabasePdfRepository()


@lru_cache
def get_similarity_repository() -> SupabaseSimilarityRepository:
    return SupabaseSimilarityRepository()


def get_embed_text_service() -> EmbedTextService:
    return EmbedTextService(
        cleaner=get_cleaner(),
        embedder=get_embedding_model(),
        repo=get_text_repository(),
    )


def get_embed_pdf_service() -> EmbedPdfService:
    return EmbedPdfService(
        chunker=get_pdf_chunker(),
        cleaner=get_cleaner(),
        embedder=get_embedding_model(),
        repo=get_pdf_repository(),
    )


def get_pdf_status_service() -> PdfStatusService:
    return PdfStatusService(
        repo=get_pdf_repository(),
    )


def get_similarity_service() -> SimilarityService:
    return SimilarityService(
        cleaner=get_cleaner(),
        embedder=get_embedding_model(),
        repo=get_similarity_repository(),
    )