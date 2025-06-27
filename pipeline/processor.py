from typing import Any, Dict, List, Tuple
from embedding.embedder_factory import EmbedderFactory
from pipeline.chunker import ChunkStrategy
from pipeline.preprocessor import TextPreprocessor


class TextProcessingPipeline:
    """
    Orchestrates the “clean → chunk → embed → assemble” workflow.
    
    Responsibilities:
      1. Receive raw text (and an optional document_id).
      2. Clean the text via TextPreprocessor.
      3. Use a supplied ChunkStrategy (e.g., SentenceBasedChunkStrategy) to split cleaned text into chunks.
      4. Use an Embedder (from EmbedderFactory) to embed every chunk (in batch).
      5. Return a dictionary containing document_id, total_chunks, and a list of chunk dicts
         of the form {"chunk_id": int, "text": str, "embedding": List[float]}.
    
    Note:
      - The pipeline does NOT store any “active” ChunkStrategy on itself. Instead, the caller
        passes a chunk_strategy instance into the `process` method for each request, avoiding
        any cross-request mutation or race conditions.
      - The Embedder is created once at initialization via the EmbedderFactory (given a model name).
    """
    def __init__(self,
                 preprocessor: TextPreprocessor,
                 embedder_name: str):
        """
        Args:
            preprocessor (TextPreprocessor): Instance responsible for cleaning raw text.
            embedder_name (str): The name/key of the embedding model to load (e.g. "all-MiniLM-L6-v2").
                                  TextProcessingPipeline will ask EmbedderFactory for a matching Embedder.
        """

        self.preprocessor = preprocessor

        self.embedder = EmbedderFactory.get_embedder(embedder_name)

    def process(self,
                raw_text: str,
                chunk_strategy: ChunkStrategy,
                options: Dict[str, Any] = None) -> Dict[str, Any]:
        
        cleaned_text = self.preprocessor.clean(raw_text)

        chunks: List[Tuple[int, str]] = chunk_strategy.split(cleaned_text)

        print("Chunking: ", chunks)


        chunk_texts: List[str] = [chunk_text for (_id, chunk_text) in chunks]

        embeddings: List[List[float]] = self.embedder.encode(chunk_texts)

        chunk_results: List[Dict[str, Any]] = []
        for (chunk_id, chunk_text), embedding_vector in zip(chunks, embeddings):
            chunk_results.append({
                "text": chunk_text,
                "embedding": embedding_vector
            })

        return {
            "total_chunks": len(chunk_results),
            "chunks": chunk_results
        }