import asyncio
import logging
import os
from typing import List, Optional
from uuid import UUID

from dotenv import load_dotenv
from supabase import create_client

from application.exceptions import PdfPersistenceError
from domain.interfaces import IPDFRepository

load_dotenv()

logger = logging.getLogger(__name__)


class SupabasePdfRepository(IPDFRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase configuration missing")

        self.client = create_client(url, key)

    async def create_pdf(self, filename: str, consultant_id: UUID) -> UUID:
        payload = {
            "filename": filename,
            "consultant_id": str(consultant_id),
            "status": "pending",
        }

        try:
            response = await asyncio.to_thread(
                lambda: self.client
                .table("pdf_files")
                .insert(payload, returning="representation")
                .execute()
            )

            rows = response.data or []

            if not rows:
                raise PdfPersistenceError("Insert succeeded but no PDF row was returned")

            pdf_id = rows[0].get("id")

            if not pdf_id:
                raise PdfPersistenceError("No id returned from pdf_files")

            return UUID(pdf_id)

        except PdfPersistenceError:
            raise

        except Exception as exc:
            logger.error("Failed to create PDF record.", exc_info=True)
            raise PdfPersistenceError("Error creating PDF record") from exc

    async def add_chunk(
        self,
        pdf_id: UUID,
        chunk_index: int,
        raw_text: str,
        cleaned_text: str,
        embedding: List[float],
    ) -> UUID:
        payload = {
            "pdf_id": str(pdf_id),
            "chunk_index": chunk_index,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "embedding": embedding,
        }

        try:
            response = await asyncio.to_thread(
                lambda: self.client
                .table("pdf_chunks")
                .insert(payload, returning="representation")
                .execute()
            )

            rows = response.data or []

            if not rows:
                raise PdfPersistenceError("Insert succeeded but no PDF chunk row was returned")

            chunk_id = rows[0].get("id")

            if not chunk_id:
                raise PdfPersistenceError("No id returned from pdf_chunks")

            return UUID(chunk_id)

        except PdfPersistenceError:
            raise

        except Exception as exc:
            logger.error("Failed to insert PDF chunk.", exc_info=True)
            raise PdfPersistenceError("Error persisting PDF chunk") from exc

    async def update_status(self, pdf_id: UUID, status: str) -> None:
        try:
            await asyncio.to_thread(
                lambda: self.client
                .table("pdf_files")
                .update({"status": status})
                .eq("id", str(pdf_id))
                .execute()
            )

        except Exception as exc:
            logger.error("Failed to update PDF status. pdf_id=%s", pdf_id, exc_info=True)
            raise PdfPersistenceError("Error updating PDF status") from exc

    async def get_status(self, pdf_id: UUID) -> Optional[str]:
        try:
            response = await asyncio.to_thread(
                lambda: self.client
                .table("pdf_files")
                .select("status")
                .eq("id", str(pdf_id))
                .maybe_single()
                .execute()
            )

            data = response.data

            if not data:
                return None

            return data.get("status")

        except Exception as exc:
            logger.error("Failed to get PDF status. pdf_id=%s", pdf_id, exc_info=True)
            raise PdfPersistenceError("Error fetching PDF status") from exc