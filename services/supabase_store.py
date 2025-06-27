import os
from typing import List
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
