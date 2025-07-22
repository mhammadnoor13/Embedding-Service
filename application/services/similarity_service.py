import logging
from typing import List
from uuid import UUID
from application.exceptions import TextCleaningError, TextEmbeddingError
from domain.entities import SimilarityResult
from domain.interfaces import IEmbeddingModel, ISimilarityRepository, ITextCleaner

logger = logging.getLogger(__name__)

class SimilarityService:
    def __init__(
        self,
        cleaner: ITextCleaner,
        embedder: IEmbeddingModel,
        repo: ISimilarityRepository
    ):
        self._cleaner = cleaner
        self._embedder = embedder
        self._repo = repo

    async def execute(
        self,
        consultant_id: UUID,
        query: str,
        k: int = 10,
        scope: str = "both"
    ) -> List[SimilarityResult]:
        try:
            cleaned = self._cleaner.clean(query)
            logger.debug("Query cleaned: %r", cleaned)
        except Exception as exc:
            logger.error("Failed to clean query %r", query, exc_info=True)
            raise TextCleaningError("Error during query cleaning") from exc
        
        try:
            vector = await self._embedder.embed(cleaned)
            logger.debug("Query embedded: dim=%d", len(vector))
        except Exception as exc:
            logger.error("Failed to embed query %r", cleaned, exc_info=True)
            raise TextEmbeddingError("Error during query embedding") from exc
        
        results = await self._repo.search(consultant_id, vector, k, scope)
        logger.info("Similarity search yielded %d results", len(results))
        return results