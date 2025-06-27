from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from config import MODEL_NAME, PROCESS_PATH
from dependencies import get_pipeline
from pipeline.chunker import  get_chunk_strategy
from pipeline.processor import TextProcessingPipeline


class ChunkOptions(BaseModel):
    chunk_strategy: Optional[str]
    chunk_size: Optional[int]
    chunk_overlap: Optional[int]
    chunk_token_limit: Optional[int]

class ProcessRequest(BaseModel):
    document_id: Optional[str] = "123"
    raw_text: str
    options: Optional[str] = None 

class ChunkResult(BaseModel):
    document_id: str | None = None
    chunk_id: int
    embedding: list[float]

class ProcessResponse(BaseModel):
    document_id: Optional[str] = None
    total_chunks: int
    chunks: list[ChunkResult]

class ApiController:
    def __init__(self, pipeline: TextProcessingPipeline):
        self.pipeline = pipeline
        self.router = APIRouter()
        
        # Register the POST /process-text endpoint
        self.router.add_api_route(
            PROCESS_PATH,
            self.process_text,
            methods=["POST"],
            response_model=ProcessResponse
        )
    
    async def process_text(
            self,
            request: ProcessRequest, 
            pipline: TextProcessingPipeline = Depends(get_pipeline)
    ) -> ProcessResponse:
        
        model = SentenceTransformer(MODEL_NAME)
        print("Embedding dim:", model.get_sentence_embedding_dimension())
                
        if not request.raw_text or request.raw_text.strip() == "":
            raise HTTPException(status_code=400, detail="raw_text must be a non-empty string")
        
        chunk_strategy = get_chunk_strategy(request.options)
        
        result = pipline.process(
            document_id = request.document_id or "",
            raw_text = request.raw_text,
            chunk_strategy = chunk_strategy
        )
        


        chunks = [ChunkResult(**chunk) for chunk in result["chunks"]]
        

        return ProcessResponse(
            document_id=result["document_id"],
            total_chunks=result["total_chunks"],
            chunks=chunks
        )




