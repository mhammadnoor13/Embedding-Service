import logging
from uuid import UUID
from application.exceptions import TextEmbeddingError, TextPersistenceError
from domain.entities import EmbeddingRecord
from domain.interfaces import IEmbeddingModel, ITextCleaner, ITextRepository
logger = logging.getLogger(__name__)


class EmbedTextService:
    def __init__(
        self,
        cleaner: ITextCleaner,
        embedder: IEmbeddingModel,
        repo: ITextRepository,
    ):
        self._cleaner = cleaner
        self._embedder = embedder
        self._repo = repo

    async def execute(self, raw_text: str, consultant_id: UUID) -> UUID:
        cleaned_text = self._cleaner.clean(raw_text)

        try:
            vector = await self._embedder.embed(cleaned_text)
            logger.debug("Text embedded successfully. dim=%d", len(vector))
        except Exception as exc:
            logger.error("Embedding model failed for text=%r", cleaned_text, exc_info=True)
            raise TextEmbeddingError("Error during text embedding") from exc


        record = EmbeddingRecord(consultant_id=consultant_id, raw_text= raw_text, embedding= vector)

        try:
            new_id = await self._repo.add(record)
            logger.info("EmbeddingRecord persisted. id=%s", new_id)
            return new_id
        except Exception as exc:
            logger.error("Failed to persist EmbeddingRecord id=%s", exc_info=True)
            raise TextPersistenceError("Error persisting embedding record") from exc

