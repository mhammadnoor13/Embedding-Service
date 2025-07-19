# from typing import List, Optional
# from uuid import uuid4
# from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
# from pydantic import BaseModel
# from pypdf import PdfReader
# from sentence_transformers import SentenceTransformer
# from config import MODEL_NAME, PROCESS_PATH, SIMILARITY_PATH
# from dependencies import get_embedder, get_pipeline, get_preprocessor
# from embedding.local_embedder import LocalEmbedder
# from pipeline.chunker import  get_chunk_strategy
# from pipeline.preprocessor import TextPreprocessor
# from pipeline.processor import TextProcessingPipeline
# import io
# from config import PROCESS_PATH
# from services import get_supabase_store
# from services.supabase_store import SupabaseChunkStore
# from postgrest import APIError


# class ChunkOptions(BaseModel):
#     chunk_strategy: Optional[str]
#     chunk_size: Optional[int]
#     chunk_overlap: Optional[int]
#     chunk_token_limit: Optional[int]

# class ProcessRequest(BaseModel):
#     document_id: Optional[str] = "123"
#     raw_text: str
#     options: Optional[str] = None 

# class ChunkResult(BaseModel):
#     document_id: str | None = None
#     chunk_id: str
#     raw_text: str
#     embedding: list[float]

# class ProcessResponse(BaseModel):
#     total_chunks: int
#     chunks: list[ChunkResult]

# class IngestResponse(BaseModel):
#     document_id: str
#     total_chunks: int

# class SearchRequest(BaseModel):
#     raw_text: str
#     top_k:Optional[int] = 5

# class Document(BaseModel):
#     id:str
#     snippet:str

# class RetrievedDocuments(BaseModel):
#     documents:List[Document]

# def extract_text_from_pdf(pdf_bytes: bytes) -> str:
#     reader = PdfReader(io.BytesIO(pdf_bytes))
#     return "\n".join(page.extract_text() or "" for page in reader.pages)

# class ApiController:
#     def __init__(self, pipeline: TextProcessingPipeline):
#         self.pipeline = pipeline
#         self.router = APIRouter()
        
#         # Register the POST /process-text endpoint
#         self.router.add_api_route(
#             PROCESS_PATH,
#             self.process_text,
#             methods=["POST"],
#             response_model=ProcessResponse
#         )

#         self.router.add_api_route(
#             f"{PROCESS_PATH}/pdf",
#             self.process_pdf,
#             methods=["POST"],
#             response_model=ProcessResponse
#         )

#         self.router.add_api_route(
#             f"{SIMILARITY_PATH}",
#             self.similarity_search,
#             methods=["POST"],
#             response_model=RetrievedDocuments
#         )
#     async def process_text(
#             self,
#             request: ProcessRequest, 
#             pipline: TextProcessingPipeline = Depends(get_pipeline)
#     ) -> ProcessResponse:
        
#         model = SentenceTransformer(MODEL_NAME)
#         print("Embedding dim:", model.get_sentence_embedding_dimension())
                
#         if not request.raw_text or request.raw_text.strip() == "":
#             raise HTTPException(status_code=400, detail="raw_text must be a non-empty string")
        
#         chunk_strategy = get_chunk_strategy(request.options)
        
#         result = pipline.process(
#             raw_text = request.raw_text,
#             chunk_strategy = chunk_strategy
#         )
        


#         chunks = [ChunkResult(**chunk) for chunk in result["chunks"]]
        

#         return ProcessResponse(
#             total_chunks=result["total_chunks"],
#             chunks=chunks
#         )

#     async def process_pdf(
#             self,
#             pdf_file: UploadFile = File(...),
#             options:  Optional[str] = None,
#             pipeline: TextProcessingPipeline = Depends(get_pipeline),
#             store: SupabaseChunkStore = Depends(get_supabase_store),

#         ) -> ProcessResponse:
#             # 1) Validate
#             if pdf_file.content_type != "application/pdf":
#                 raise HTTPException(400, "Only PDF files are supported")
#             data = await pdf_file.read()
#             if not data:
#                 raise HTTPException(400, "Uploaded PDF is empty")

#             # 2) Extract text
#             reader = PdfReader(io.BytesIO(data))
#             raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
#             if not raw_text.strip():
#                 raise HTTPException(400, "Could not extract any text from PDF")

#             # 3) Now call the pipeline directly (instead of routing through process_text)
#             model = SentenceTransformer(MODEL_NAME)
#             print("Embedding dim:", model.get_sentence_embedding_dimension())
#             chunk_strategy = get_chunk_strategy(options)

#             result = pipeline.process(
#                 raw_text       = raw_text,
#                 chunk_strategy = chunk_strategy
#             )
#             raw_chunks = result["chunks"]


#             records = [
#                 {
#                 "raw_text":  chunk["text"],
#                 "embedding": chunk["embedding"],
#                 }
#                 for chunk in raw_chunks
#             ]

#             try:
#                 inserted = store.insert_chunks(records)
#             except APIError as e:
#                 raise HTTPException(502, detail=f"DB insert failed: {e}")



#             # 4) map them into your response model (if you want to return chunk_ids)
#             chunks = []
#             for c, ins in zip(raw_chunks, inserted):
#                 chunks.append(ChunkResult(
#                     chunk_id   = ins["chunk_id"],    # the DB‐generated UUID
#                     raw_text   = c["text"],
#                     embedding  = c["embedding"],
#                 ))

#             return ProcessResponse(
#                 total_chunks = result["total_chunks"],
#                 chunks       = chunks
#             )
#     async def similarity_search(
#             self,
#             request: SearchRequest,
#             preprocessor: TextPreprocessor = Depends(get_preprocessor),
#             embedder: LocalEmbedder = Depends(get_embedder),
#             store: SupabaseChunkStore = Depends(get_supabase_store),
#     ) -> RetrievedDocuments:
#         clean_text = preprocessor.clean(request.raw_text)
#         embedding = embedder.encode([clean_text])[0]
#         try:
#             similar_texts = store.similarity_search(embedding, request.top_k)
#         except Exception as e:
#             # wrap any RPC/db errors as a 502
#             raise HTTPException(status_code=502, detail=f"Similarity search failed: {e}")
        
#         documents = [
#             Document(id=str(i), snippet=text)
#             for i, text in enumerate(similar_texts)
#         ]
#         return RetrievedDocuments(documents=documents)



