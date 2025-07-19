import logging
import os
from uuid import UUID
from dotenv import load_dotenv
from supabase import SupabaseException, create_client
from application.exceptions import TextPersistenceError
from domain.interfaces import IPDFRepository

load_dotenv("env")
logger = logging.getLogger(__name__)

class SupabasePdfRepository(IPDFRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase config missing")
        self.client = create_client(url, key)

    async def create_pdf(self, filename):
        payload = {"filename": filename}
        try:
            resp = self.client \
                .table("pdf_files") \
                .insert(payload, returning="representation") \
                .execute()
            rows = resp.data or []
            if not rows:
                raise TextPersistenceError("Failed to create pdf_files row")
            return UUID(rows[0]["id"])
        except SupabaseException as sb:
            logger.error("Supabase create_pdf failed", exc_info=True)
            raise TextPersistenceError("Error creating PDF record") from sb

    async def add_chunk(self, pdf_id, chunk_index, raw_text, embedding):
        payload = {
            "pdf_id":      str(pdf_id),
            "chunk_index": chunk_index,
            "raw_text":    raw_text,
            "embedding":   embedding,
        }

        try:
            resp = self.client \
                .table("pdf_chunks") \
                .insert(payload, returning="representation")\
                .execute()
            rows = resp.data or []
            if not rows:
                raise TextPersistenceError("Failed to insert pdf_chunk")
            return UUID(rows[0]["id"])
        except SupabaseException as sb:
            logger.error("Supabase add_chunk failed", exc_info=True)
            raise TextPersistenceError("Error persisting PDF chunk") from sb
        
    async def update_status(self, pdf_id: UUID, status: str) -> None:
        try:
            self.client \
                .table("pdf_files") \
                .update({"status": status}) \
                .eq("id", str(pdf_id)) \
                .execute()
        except SupabaseException as sb:
            logger.error("Supabase update_status failed", exc_info=True)
            raise TextPersistenceError("Error updating PDF status") from sb