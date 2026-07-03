from uuid import UUID

from application.exceptions import PdfNotFoundError, PdfPersistenceError
from domain.interfaces import IPDFRepository


class PdfStatusService:
    def __init__(self, repo: IPDFRepository):
        self._repo = repo

    async def execute(self, pdf_id: UUID) -> str:
        try:
            status = await self._repo.get_status(pdf_id)
        except Exception as exc:
            raise PdfPersistenceError("Could not fetch PDF status") from exc

        if status is None:
            raise PdfNotFoundError("PDF not found")

        return status