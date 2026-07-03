import asyncio
import logging
import math
import os
from typing import Any, List

from dotenv import load_dotenv
from huggingface_hub import InferenceClient, InferenceTimeoutError

from application.exceptions import TextEmbeddingError
from domain.interfaces import IEmbeddingModel

load_dotenv()

logger = logging.getLogger(__name__)


class HFEmbeddingModel(IEmbeddingModel):
    def __init__(self):
        self._model_name = os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        self._hf_token = os.getenv("HF_TOKEN")
        self._expected_dimension = int(os.getenv("EMBEDDING_DIMENSION", "384"))

        if not self._hf_token:
            logger.critical("Missing HF_TOKEN in environment")
            raise RuntimeError("HFEmbeddingModel misconfigured: missing HF_TOKEN")

        self._client = InferenceClient(
            model=self._model_name,
            token=self._hf_token,
        )

        logger.info("HF embedding model configured: %s", self._model_name)

    async def embed(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise TextEmbeddingError("Cannot embed empty text")

        try:
            response = await asyncio.to_thread(
                self._client.feature_extraction,
                text,
                truncate=True,
            )

            vector = self._extract_vector(response)
            vector = self._normalize(vector)

            if len(vector) != self._expected_dimension:
                raise TextEmbeddingError(
                    f"Unexpected embedding dimension: got {len(vector)}, "
                    f"expected {self._expected_dimension}"
                )

            logger.debug("HF embedding successful. dim=%d", len(vector))
            return vector

        except InferenceTimeoutError as exc:
            logger.error("Hugging Face inference timed out.", exc_info=True)
            raise TextEmbeddingError("Embedding request timed out") from exc

        except TextEmbeddingError:
            raise

        except Exception as exc:
            logger.error("Unexpected error during Hugging Face embedding.", exc_info=True)
            raise TextEmbeddingError("Unexpected error in embedding model") from exc

    def _extract_vector(self, response: Any) -> List[float]:
        """
        Hugging Face feature_extraction can return different shapes depending
        on the model/provider:
        - [dim]
        - [[dim]]
        - [[tokens, dim]]
        This method converts the response into one single embedding vector.
        """
        data = response.tolist() if hasattr(response, "tolist") else response

        if not isinstance(data, list) or not data:
            raise TextEmbeddingError("Invalid embedding response from Hugging Face")

        # Case 1: already a single vector: [0.1, 0.2, ...]
        if self._is_number_list(data):
            return [float(x) for x in data]

        # Case 2: one wrapped vector: [[0.1, 0.2, ...]]
        if len(data) == 1 and isinstance(data[0], list) and self._is_number_list(data[0]):
            return [float(x) for x in data[0]]

        # Case 3: token embeddings: [[token_dim], [token_dim], ...]
        # We use mean pooling to produce one vector.
        if all(isinstance(row, list) and self._is_number_list(row) for row in data):
            return self._mean_pool(data)

        # Case 4: extra batch dimension: [[[...], [...]]]
        if len(data) == 1 and isinstance(data[0], list):
            return self._extract_vector(data[0])

        raise TextEmbeddingError("Unsupported embedding response shape from Hugging Face")

    def _mean_pool(self, token_vectors: List[List[float]]) -> List[float]:
        if not token_vectors:
            raise TextEmbeddingError("Cannot mean-pool empty token vectors")

        dimension = len(token_vectors[0])

        if dimension == 0:
            raise TextEmbeddingError("Token vectors have empty dimension")

        for vector in token_vectors:
            if len(vector) != dimension:
                raise TextEmbeddingError("Inconsistent token vector dimensions")

        pooled = []

        for i in range(dimension):
            pooled.append(sum(vector[i] for vector in token_vectors) / len(token_vectors))

        return [float(x) for x in pooled]

    def _normalize(self, vector: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vector))

        if norm == 0:
            raise TextEmbeddingError("Embedding vector has zero norm")

        return [x / norm for x in vector]

    def _is_number_list(self, value: list) -> bool:
        return all(isinstance(x, (int, float)) for x in value)