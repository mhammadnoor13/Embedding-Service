from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from api.controller import ApiController
from config import MODEL_NAME
from pipeline.preprocessor import TextPreprocessor
from pipeline.processor import TextProcessingPipeline

preprocessor = TextPreprocessor(lowercase=False)
pipeline = TextProcessingPipeline(preprocessor, MODEL_NAME)
controller = ApiController(pipeline)

app = FastAPI(title="Text‐Embedding Service")
app.include_router(controller.router)


