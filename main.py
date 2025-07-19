import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from application.services.embed_text import EmbedTextService
from infrastrcture.embedding.hf_embedding import HFEmbeddingModel
from infrastrcture.supabase_repository.supabase_text_repository import SupaBaseTextRepository
from api.controllers.embed_text import router as embed_router
from api.controllers.embed_pdf import router as embed_pdf_router
from api.controllers.similarity import router as similarity_router



app = FastAPI(title="Text‐Embedding Service")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app.include_router(embed_router)
app.include_router(embed_pdf_router)
app.include_router(similarity_router)

# @app.on_event("startup")
# async def load_model():
#     # This runs *after* UVicorn has started the server and emitted its logs.
#     preprocessor = TextPreprocessor(lowercase=False)
#     pipeline     = TextProcessingPipeline(preprocessor, MODEL_NAME)
#     controller   = ApiController(pipeline)
#     app.include_router(controller.router)

@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}