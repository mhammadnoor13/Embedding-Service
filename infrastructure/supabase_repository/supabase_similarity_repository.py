import asyncio
import logging
import os
from typing import List
from uuid import UUID

from dotenv import load_dotenv
from supabase import create_client

from domain.entities import SimilarityResult
from domain.interfaces import ISimilarityRepository

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseSimilarityRepository(ISimilarityRepository):
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.critical("Missing SUPABASE_URL or SUPABASE_KEY")
            raise RuntimeError("Supabase configuration missing")

        self.client = create_client(url, key)

    async def search(
        self,
        consultant_id: UUID,
        embedding: List[float],
        k: int,
        scope: str,
        min_similarity: float,
    ) -> List[SimilarityResult]:
        params = {
            "p_consultant_id": str(consultant_id),
            "p_query_embedding": embedding,
            "p_match_count": k,
            "p_scope": scope,
            "p_min_similarity": min_similarity,
        }

        try:
            response = await asyncio.to_thread(
                lambda: self.client
                .rpc("similarity_search", params)
                .execute()
            )

            rows = response.data or []

        except Exception as exc:
            logger.error("Supabase similarity_search RPC failed.", exc_info=True)
            raise

        results: List[SimilarityResult] = []

        for row in rows:
            results.append(
                SimilarityResult(
                    id=UUID(row["id"]),
                    source=row["source"],
                    raw_text=row["raw_text"],
                    pdf_id=UUID(row["pdf_id"]) if row.get("pdf_id") else None,
                    similarity=float(row["similarity"]),
                )
            )

        return results