import os
from typing import List
from postgrest import APIError
from supabase import create_client, Client
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
# 3.1 Define the shape of a chunk record
class ChunkRecord(BaseModel):
    chunk_id: str
    raw_text: str
    embedding: List[float]

# 3.2 Wrap Supabase calls in a class
class SupabaseChunkStore:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        self.client: Client = create_client(url, key)

    def insert_chunks(self, records: List[ChunkRecord]):
        
        """
        insert a batch of chunk records into the 'chunks' table.
        """

        res = (
            self.client
                .table("chunks")
                .insert(records, returning="representation")
                .execute()
        )
        
        return res.data

    def similarity_search(self, embedding: List[float], top_k: int) -> List[str]:
        """
        Call the match_chunks RPC to get the top_k most similar chunks,
        and return just their raw_text fields.
        """
        try:
            res = (
                self.client
                    .rpc("match_chunks", {"query_embedding": embedding, "match_count": top_k})
                    .execute()
            )
        except APIError as e:
            raise
        print("Returned rows:", len(res.data))
        # res.data is a list of dicts with keys chunk_id, raw_text, embedding
        return [row["raw_text"] for row in res.data]