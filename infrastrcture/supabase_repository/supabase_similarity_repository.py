import asyncio
import logging
import os
from typing import List
from uuid import UUID

from supabase import SupabaseException, create_client
from domain.entities import SimilarityResult
from domain.interfaces import ISimilarityRepository
logger = logging.getLogger(__name__)


class SupabaseSimilarityRepository(ISimilarityRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase config missing")
        self.client = create_client(url, key)

    async def search(
        self,
        embedding: List[float],
        k: int,
        scope: str  # 'text' | 'pdf' | 'both'
    ) -> List[SimilarityResult]:
        
        loop = asyncio.get_running_loop()
        params = {
            "query_embedding": embedding,
            "k": k,
            "scope": scope,
        }
        try:
            resp = await loop.run_in_executor(
                None,
                lambda: self.client.rpc("similarity_search", params).execute()
            )
            rows = resp.data or []
            breakpoint()

        except SupabaseException as sb:
            logger.error("Supabase similarity_search RPC failed", exc_info=True)
            raise
        except Exception as exc:
            logger.error("Unexpected error in similarity search", exc_info=True)
            raise

        results: List[SimilarityResult] = []
        for r in rows:
            results.append(
                SimilarityResult(
                    id=UUID(r["id"]),
                    source=r["source"],
                    raw_text=r["raw_text"],
                    pdf_id=UUID(r["pdf_id"]) if r.get("pdf_id") else None,
                    similarity=float(r["similarity"]),
                )
            )
        
        return results