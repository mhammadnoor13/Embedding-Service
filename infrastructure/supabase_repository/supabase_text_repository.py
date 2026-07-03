import asyncio
import logging
import os
from dataclasses import asdict
from uuid import UUID

from dotenv import load_dotenv
from supabase import create_client

from application.exceptions import TextPersistenceError
from domain.entities import EmbeddingRecord
from domain.interfaces import ITextRepository

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseTextRepository(ITextRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase configuration missing")

        self.client = create_client(url, key)

    async def add(self, record: EmbeddingRecord) -> UUID:
        payload = asdict(record)
        payload["consultant_id"] = str(payload["consultant_id"])

        try:
            response = await asyncio.to_thread(
                lambda: self.client
                .table("previous_cases_embeddings")
                .insert(payload, returning="representation")
                .execute()
            )

            rows = response.data or []

            if not rows:
                raise TextPersistenceError("Insert succeeded but no row was returned")

            new_id = rows[0].get("id")

            if not new_id:
                raise TextPersistenceError("No id returned from Supabase")

            return UUID(new_id)

        except TextPersistenceError:
            raise

        except Exception as exc:
            logger.error("Failed to insert text embedding.", exc_info=True)
            raise TextPersistenceError("Error persisting text embedding") from exc


