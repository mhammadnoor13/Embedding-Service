import asyncio
import logging
import os
from typing import List

from sentence_transformers import SentenceTransformer

from application.exceptions import TextEmbeddingError
from domain.interfaces import IEmbeddingModel

logger = logging.getLogger(__name__)


class LocalSentenceTransformerEmbedding(IEmbeddingModel):
    def __init__(self):
        model_name = os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        try:
            self._model = SentenceTransformer(model_name)
            self._model_name = model_name
            logger.info("Loaded embedding model: %s", model_name)
        except Exception as exc:
            logger.critical("Failed to load embedding model: %s", model_name, exc_info=True)
            raise RuntimeError("Embedding model could not be loaded") from exc

    async def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise TextEmbeddingError("Cannot embed empty text")

        try:
            vector = await asyncio.to_thread(
                self._model.encode,
                text,
                normalize_embeddings=True,
            )

            return vector.tolist()

        except Exception as exc:
            logger.error("Local embedding generation failed.", exc_info=True)
            raise TextEmbeddingError("Error generating local embedding") from exc