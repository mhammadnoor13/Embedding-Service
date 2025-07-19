import os
import logging
from typing import List, Optional

from huggingface_hub import InferenceClient


class HFEmbeddingClient:
    """
    Implements the Embedder protocol by calling HF’s InferenceClient.

    - No local downloads: calls the endpoint you specify.
    - Free tier (subject to HF API limits).
    - Handles both per-token and pooled responses.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """
        Args:
            model_name: Hugging Face repo ID (e.g. "Qwen/Qwen3-Embedding-8B").
            api_key: Your HF API key. If not supplied, will read HF_HUB_API_TOKEN.
            provider: (Optional) e.g. "nebius", "huggingface" etc.
        Raises:
            RuntimeError: if no API key is found.
        """
    def encode(self, texts: List[str]) -> List[List[float]]:
        
        embeddings: List[List[float]] = []
       

        return embeddings
