from abc import ABC, abstractmethod
import re
from typing import Dict, List, Optional, Tuple

class ChunkStrategy(ABC):
    
    @abstractmethod
    def split(self, text: str) -> List[Tuple[int, str]]:
        pass


class SentenceBasedChunkStrategy(ChunkStrategy):
    """
    Splits text into chunks by grouping complete sentences until a maximum
    character threshold is reached, then starts a new chunk.
    
    - Uses a simple regex to split on sentence boundaries (".", "?", "!" followed by whitespace).
    - If any single sentence exceeds `max_characters`, it becomes its own chunk.
    """
    _SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[\.\?\!])\s+")

    def split(self, text: str) -> List[Tuple[int, str]]:

        sentences = self._SENTENCE_SPLIT_REGEX.split(text)
        
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks: List[Tuple[int, str]] = [
            (idx, sentence) for idx, sentence in enumerate(sentences)
        ]

        return chunks


def get_chunk_strategy(options: Optional[Dict] = None):
    strategy_name = None
    if options and isinstance(options, dict):
        strategy_name = options.get("chunk_strategy")
    
    if strategy_name == "sentence":
        return SentenceBasedChunkStrategy()
    else:
        return SentenceBasedChunkStrategy()


    

