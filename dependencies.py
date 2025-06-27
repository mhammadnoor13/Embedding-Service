from fastapi import Depends
from config import MODEL_NAME
from embedding.local_embedder import LocalEmbedder
from pipeline.preprocessor import TextPreprocessor
from pipeline.processor import TextProcessingPipeline


def get_preprocessor() -> TextPreprocessor:
    return TextPreprocessor()

def get_embedder() -> LocalEmbedder:
    return LocalEmbedder(MODEL_NAME)

def get_pipeline(
    preprocessor: TextPreprocessor = Depends(get_preprocessor),
    embedder_name: str = MODEL_NAME
) -> TextProcessingPipeline:
    # Create pipeline with a default chunk strategy (used only if no override)
    return TextProcessingPipeline(preprocessor, embedder_name)
