"""Import batch schemas — request bodies and API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import Page

PREVIEW_LIMIT = 200


class ImportRowRead(BaseModel):
    """One validated spreadsheet row as returned to the client."""

    id: int
    row_number: int
    status: str
    raw_data: dict[str, Any] = {}
    normalized_data: dict[str, Any] = {}
    error_code: str | None = None
    error_message: str | None = None
    warnings: list[str] = []
    target_id: int | None = None

    model_config = {"from_attributes": True}


class ImportSummary(BaseModel):
    """Row counters shown in the wizard header."""

    total_rows: int
    ok_rows: int
    warning_rows: int
    error_rows: int
    imported_rows: int
    customers_created: int = 0


class ImportBatchRead(BaseModel):
    """A batch plus its summary and a preview of its rows."""

    id: int
    entity_type: str
    status: str
    source_layout: str
    file_name: str
    warnings: list[str] = []
    error_message: str | None = None
    created_at: datetime
    committed_at: datetime | None = None
    summary: ImportSummary
    preview: list[ImportRowRead] = []

    @classmethod
    def from_model(cls, batch, *, preview: list | None = None) -> "ImportBatchRead":
        """Build the response from an ORM batch object.

        ``preview`` must be passed explicitly by callers that loaded the rows;
        reading ``batch.rows`` implicitly would trigger a lazy load and explode
        in the async session.
        """
        rows = sorted(preview or [], key=lambda row: row.row_number)[:PREVIEW_LIMIT]
        return cls(
            id=batch.id,
            entity_type=batch.entity_type,
            status=batch.status,
            source_layout=batch.source_layout,
            file_name=batch.file_name,
            warnings=list(batch.warnings or []),
            error_message=batch.error_message,
            created_at=batch.created_at,
            committed_at=batch.committed_at,
            summary=ImportSummary(
                total_rows=batch.total_rows,
                ok_rows=batch.ok_rows,
                warning_rows=batch.warning_rows,
                error_rows=batch.error_rows,
                imported_rows=batch.imported_rows,
                customers_created=batch.customers_created,
            ),
            preview=[ImportRowRead.model_validate(row) for row in rows],
        )


class ImportBatchPage(Page[ImportBatchRead]):
    """Paginated import history."""

    pass


class ImportRowPage(Page[ImportRowRead]):
    """Paginated import rows."""

    pass


class ImportCommitRequest(BaseModel):
    """Body of the commit endpoint."""

    skip_error_rows: bool = True
