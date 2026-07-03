class EmbeddingServiceError(Exception):
    """Base class for application-level errors in the Embedding Service."""
    pass


class TextCleaningError(EmbeddingServiceError):
    """Raised when text cleaning fails."""
    pass


class TextEmbeddingError(EmbeddingServiceError):
    """Raised when embedding generation fails."""
    pass


class TextPersistenceError(EmbeddingServiceError):
    """Raised when saving text embeddings fails."""
    pass


class PdfProcessingError(EmbeddingServiceError):
    """Base class for errors during PDF processing."""
    pass


class PdfChunkingError(PdfProcessingError):
    """Raised when splitting a PDF into chunks fails."""
    pass


class PdfCleaningError(PdfProcessingError):
    """Raised when cleaning a PDF chunk fails."""
    pass


class PdfEmbeddingError(PdfProcessingError):
    """Raised when embedding a PDF chunk fails."""
    pass


class PdfPersistenceError(PdfProcessingError):
    """Raised when saving a PDF or its chunks fails."""
    pass


class PdfNotFoundError(PdfProcessingError):
    """Raised when a PDF record cannot be found."""
    pass