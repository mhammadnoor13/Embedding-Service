import logging
import os
from typing import List
from dotenv import load_dotenv
from huggingface_hub import InferenceClient, InferenceTimeoutError
from application.exceptions import TextEmbeddingError
from domain.interfaces import IEmbeddingModel
load_dotenv(".env")

logger = logging.getLogger(__name__)

class HFEmbeddingModel(IEmbeddingModel):
    def __init__(self):
        model_name= os.getenv("MODEL_NAME")
        hf_token= os.getenv("HF_TOKEN")
        if not model_name or not hf_token:
            logger.critical("Missing MODEL_NAME or HF_TOKEN in environment")
            raise RuntimeError("HFEmbeddingModel misconfigured")
        self._client = InferenceClient(model_name, token = hf_token)
    
    async def embed(self, text: str) -> List[float]:
        try:
            resp = self._client.feature_extraction(text, truncate= True)
            embeddings = resp[0].tolist()            
            logger.debug("HF embedding successful (dim=%d)", len(embeddings))
            return embeddings
        except InferenceTimeoutError as te:
            logger.error("Hugging Face inference timed out for text=%r", text, exc_info=True)
            raise TextEmbeddingError("Embedding request timed out") from te

        except Exception as exc:
            logger.error("Unexpected error during HF embedding", exc_info=True)
            raise TextEmbeddingError("Unexpected error in embedding model") from exc