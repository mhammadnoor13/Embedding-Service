# embedding/embedder_factory.py

from typing import Protocol
from embedding.local_embedder import LocalEmbedder
from embedding.remote_embedder import HFEmbeddingClient


class Embedder(Protocol):
    """
    Protocol defining the interface for any Embedder implementation.
    Any concrete Embedder must provide an `encode` method that takes a list of strings
    and returns a list of float‐vector embeddings (one per input string).
    """

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        Encode a batch of input texts into embeddings.

        Args:
            texts (list[str]): A list of strings to embed.

        Returns:
            list[list[float]]: A list of embedding vectors (each a list of floats),
                               in the same order as the input texts.
        """
        


class EmbedderFactory:
    """
    Simple factory for instantiating Embedder implementations by name.
    Currently supports:
      - "local": uses a LocalEmbedder (SentenceTransformer under the hood)
    
    If you need to add new embedding backends (e.g. a remote HTTP API),
    add a new key‐to‐class mapping in `get_embedder`.
    """

    @staticmethod
    def get_embedder(name: str) -> Embedder:
        """
        Given a model name or key, return an object implementing the Embedder interface.

        Args:
            name (str): Identifier for which embedding implementation to use.
                        For example: "local" or a specific model name.

        Returns:
            Embedder: An instance of a class that implements `encode(...)`.
        """
        # For now, treat any non‐empty string as “use the local SentenceTransformer model.”
        # The LocalEmbedder constructor will interpret `name` as the SentenceTransformer model name.
        #
        # In the future, if you have other backends (e.g. an HTTP service, or a GPU‐optimized server),
        # you can do something like:
        #   if name.startswith("remote:"):
        #       return RemoteEmbedder(endpoint=name.split(":", 1)[1])
        #   elif name == "local":
        #       return LocalEmbedder(default_model_name)
        #   elif name.startswith("local:"):
        #       return LocalEmbedder(model_name=name.split(":", 1)[1])
        #   else:
        #       raise ValueError(f"Unknown embedder: {name}")
        #
        # Currently, we simply pass `name` to LocalEmbedder and let it attempt to load that model.
        return HFEmbeddingClient(model_name=name)
