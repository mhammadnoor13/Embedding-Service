class EmbedTextError(Exception):
    """Base class for all errors in the Embed Text flow."""
    pass

class TextCleaningError(EmbedTextError):
    """Raised when cleaning text (or query) fails."""
    pass

class TextEmbeddingError(EmbedTextError):
    """Raised when the embedding model fails."""
    pass

class TextPersistenceError(EmbedTextError):
    """Raised when saving to the repository fails."""
    pass

class PdfProcessingError(Exception):
    """Base class for errors during PDF processing (chunk→embed→persist)."""
    pass

class PdfChunkingError(PdfProcessingError):
    """Raised if splitting the PDF into text chunks fails."""
    pass

class PdfEmbeddingError(PdfProcessingError):
    """Raised if embedding any chunk fails."""
    pass

class PdfPersistenceError(PdfProcessingError):
    """Raised if saving any chunk to the database fails."""
    pass
