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
        repo: ISimilarityRepository,
    ):
        self._cleaner = cleaner
        self._embedder = embedder
        self._repo = repo

    async def execute(
        self,
        consultant_id: UUID,
        query: str,
        k: int = 10,
        scope: str = "both",
        min_similarity: float = 0.70,
    ) -> List[SimilarityResult]:
        try:
            cleaned_query = self._cleaner.clean(query)
            logger.debug("Query cleaned successfully.")
        except Exception as exc:
            logger.error("Failed to clean query.", exc_info=True)
            raise TextCleaningError("Error during query cleaning") from exc

        try:
            vector = await self._embedder.embed(cleaned_query)
            logger.debug("Query embedded successfully. dim=%d", len(vector))
        except Exception as exc:
            logger.error("Failed to embed query.", exc_info=True)
            raise TextEmbeddingError("Error during query embedding") from exc

        results = await self._repo.search(
            consultant_id=consultant_id,
            embedding=vector,
            k=k,
            scope=scope,
            min_similarity=min_similarity,
        )

        logger.info("Similarity search yielded %d results", len(results))
        return results