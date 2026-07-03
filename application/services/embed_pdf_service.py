import logging
from uuid import UUID

from application.exceptions import PdfChunkingError, PdfCleaningError, PdfEmbeddingError, PdfPersistenceError, PdfProcessingError
from domain.interfaces import IEmbeddingModel, IPDFChunker, IPDFRepository, ITextCleaner


logger = logging.getLogger(__name__)

class EmbedPdfService:
    def __init__(self,
        chunker: IPDFChunker,
        cleaner: ITextCleaner,
        embedder: IEmbeddingModel,
        repo: IPDFRepository,
    ):
        self._chunker = chunker
        self._cleaner = cleaner
        self._embedder = embedder
        self._repo = repo

    async def execute(
        self, 
        pdf_bytes, 
        consultant_id: UUID, 
        filename: str = "No-Name",
        ) -> UUID:
        
        try:
            pdf_id = await self._repo.create_pdf(filename, consultant_id)
            logger.info("Started PDF processing. pdf_id=%s filename=%s", pdf_id, filename)
        except Exception as exc:
            logger.error("Failed to create PDF record.", exc_info=True)
            raise PdfPersistenceError("Error creating PDF record") from exc

        try:
            chunks = self._chunker.chunk(pdf_bytes)

            if not chunks:
                raise PdfChunkingError("No text could be extracted from the PDF")

            logger.debug("PDF split into %d chunks. pdf_id=%s", len(chunks), pdf_id)

        except PdfChunkingError:
            await self._repo.update_status(pdf_id, "error")
            raise

        except Exception as exc:
            await self._repo.update_status(pdf_id, "error")
            logger.error("PDF chunking failed. pdf_id=%s", pdf_id, exc_info=True)
            raise PdfChunkingError("Unable to split PDF into chunks") from exc

        for idx, raw_text in enumerate(chunks):
            try:
                cleaned_text = self._cleaner.clean(raw_text)
            except Exception as exc:
                await self._repo.update_status(pdf_id, "error")
                logger.error("Cleaning failed for chunk %d. pdf_id=%s", idx, pdf_id, exc_info=True)
                raise PdfCleaningError(f"Error cleaning chunk {idx}") from exc

            try:
                vector = await self._embedder.embed(cleaned_text)
            except Exception as exc:
                await self._repo.update_status(pdf_id, "error")
                logger.error("Embedding failed for chunk %d. pdf_id=%s", idx, pdf_id, exc_info=True)
                raise PdfEmbeddingError(f"Error embedding chunk {idx}") from exc

            try:
                await self._repo.add_chunk(
                    pdf_id=pdf_id,
                    chunk_index=idx,
                    raw_text=raw_text,
                    cleaned_text=cleaned_text,
                    embedding=vector,
                )
                logger.debug("Persisted chunk %d. pdf_id=%s", idx, pdf_id)
            except Exception as exc:
                await self._repo.update_status(pdf_id, "error")
                logger.error("Persistence failed for chunk %d. pdf_id=%s", idx, pdf_id, exc_info=True)
                raise PdfPersistenceError(f"Error saving chunk {idx}") from exc

        await self._repo.update_status(pdf_id, "ready")
        logger.info("Completed PDF processing. pdf_id=%s", pdf_id)

        return pdf_id