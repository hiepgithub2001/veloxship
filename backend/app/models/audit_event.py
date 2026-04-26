"""Audit event model."""

from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AuditEvent(Base):
    """Generic audit trail — maps to `audit_events` table."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True,
    )
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<AuditEvent id={self.id} action={self.action}>"
