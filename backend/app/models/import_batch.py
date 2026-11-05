"""Import batch and row models — audit trail for Excel imports."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

BATCH_STATUSES = (
    "validating",
    "validated",
    "committing",
    "completed",
    "partially_completed",
    "failed",
)
ROW_STATUSES = ("ok", "warning", "error", "imported", "skipped")


class ImportBatch(Base):
    """One uploaded workbook and the outcome of validating/committing it."""

    __tablename__ = "import_batches"
    __table_args__ = (
        CheckConstraint("entity_type IN ('bill')", name="entity_type"),
        CheckConstraint(
            "status IN ('validating', 'validated', 'committing', 'completed', "
            "'partially_completed', 'failed')",
            name="status",
        ),
        Index("ix_import_batches_creator", "created_by", "created_at"),
        Index("ix_import_batches_hash", "file_hash"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False, default="bill")
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_layout: Mapped[str] = mapped_column(
        String(32), nullable=False, default="legacy_logex"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="validating"
    )

    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ok_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    warning_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    customers_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    warnings: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    options: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    committed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    rows = relationship(
        "ImportRow",
        back_populates="batch",
        cascade="all, delete-orphan",
        order_by="ImportRow.row_number",
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ImportBatch id={self.id} status={self.status} rows={self.total_rows}>"


class ImportRow(Base):
    """One spreadsheet row: the raw cells, the normalised payload and the verdict."""

    __tablename__ = "import_rows"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ok', 'warning', 'error', 'imported', 'skipped')",
            name="status",
        ),
        Index("ux_import_rows_batch_row", "batch_id", "row_number", unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)

    raw_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    normalized_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    status: Mapped[str] = mapped_column(String(10), nullable=False, default="ok")
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    target_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    batch = relationship("ImportBatch", back_populates="rows")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ImportRow batch={self.batch_id} row={self.row_number} status={self.status}>"
