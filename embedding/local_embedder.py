# embedding/local_embedder.py

from sentence_transformers import SentenceTransformer
from typing import List
import logging


class LocalEmbedder:
    """
    Implements the Embedder protocol using a local SentenceTransformer model.
    
    Responsibilities:
      - Load the specified SentenceTransformer model once at initialization.
      - Expose an `encode` method that takes a list of strings and returns their embeddings.
      - Handle errors in model loading or encoding and log appropriately.
    """

    def __init__(self, model_name: str):
        """
        Initialize the LocalEmbedder by loading the SentenceTransformer model.
        
        Args:
            model_name (str): The Hugging Face model identifier (e.g., "all-MiniLM-L6-v2")
                              or a local path to a pre-downloaded model directory.
        
        Raises:
            RuntimeError: If the model cannot be loaded.
        """
        if not isinstance(model_name, str):
            raise TypeError(
                f"LocalEmbedder expected str model_name, got {type(model_name).__name__}"
            )
        self.model_name = model_name
        try:
            # Load the model (this downloads from HF if not cached locally)
            self.model = SentenceTransformer(model_name)
            print("model name: ",model_name)
            logging.info(f"✅ Loaded SentenceTransformer model '{model_name}'.")
        except Exception as e:
            logging.error(f"❌ Failed to load SentenceTransformer model '{model_name}': {e}")
            raise RuntimeError(f"Could not load embedding model '{model_name}'.") from e

    def encode(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a batch of texts into their corresponding embeddings.
        
        Args:
            texts (List[str]): A list of input strings to embed.
        
        Returns:
            List[List[float]]: A list of embedding vectors (one per input string).
        
        Raises:
            ValueError: If `texts` is empty or contains non-string entries.
            RuntimeError: If the embedding operation fails at runtime.
        """
        if not isinstance(texts, list) or any(not isinstance(t, str) for t in texts):
            raise ValueError("Input to LocalEmbedder.encode must be a list of strings.")

        try:
            # The model.encode(...) call returns a numpy array or list of floats by default.
            embeddings = self.model.encode(texts)
            
            # Convert any numpy arrays to Python lists for JSON serialization
            # If embeddings is already a list of lists, this is a no-op.
            return [emb.tolist() if hasattr(emb, "tolist") else emb for emb in embeddings]
        except Exception as e:
            logging.error(f"❌ Error during embedding on model '{self.model_name}': {e}")
            raise RuntimeError("Embedding operation failed.") from e
