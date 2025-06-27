from .supabase_store import SupabaseChunkStore

def get_supabase_store() -> SupabaseChunkStore:
    return SupabaseChunkStore()
