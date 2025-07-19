import logging
import os
from typing import List
from uuid import UUID
from supabase import SupabaseException, create_client
from application.exceptions import TextPersistenceError
from domain.entities import EmbeddingRecord
from domain.interfaces import ITextRepository
from dotenv import load_dotenv
load_dotenv(".env")

logger = logging.getLogger(__name__)


class SupaBaseTextRepository(ITextRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase configuration missing")
        self.client = create_client(url, key)
        

    async def add(self, record: EmbeddingRecord ) -> UUID:
        payload = record.dict()
        try:
            resp = (self.client.table("previous_cases_embeddings").insert(payload, returning="representation").execute())
            rows = resp.data or []

            if not rows:
                raise TextPersistenceError("Insert succeeded but no row was returned")
            new_id = rows[0].get("case_id")
            if not new_id:
                raise ValueError("No `id` returned from Supabase")
            return UUID(new_id)
        except SupabaseException as sb_exc:
            logger.error("Supabase insert failed: %s", sb_exc, exc_info=True)
            raise
        except Exception as exc:
            logger.error("Unexpected error in SupabaseTextRepository.add: %s", exc, exc_info=True)
            raise
