import logging

from fastapi import FastAPI

from api.controllers.embed_text_controller import router as embed_text_router
from api.controllers.embed_pdf_controller import router as embed_pdf_router
from api.controllers.similarity_controller import router as similarity_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


app = FastAPI(
    title="AI-Aided Consultant Platform - Embedding Service",
    version="1.0.0",
    description="Service responsible for text/PDF embedding, vector persistence, and similarity search.",
)


app.include_router(embed_text_router)
app.include_router(embed_pdf_router)
app.include_router(similarity_router)


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok"}