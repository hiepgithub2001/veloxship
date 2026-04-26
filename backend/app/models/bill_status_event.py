"""Bill status event model."""

from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BillStatusEvent(Base):
    """Status change history — maps to `bill_status_events` table."""

    __tablename__ = "bill_status_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False,
    )
    from_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_status: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    bill = relationship("Bill", back_populates="status_events")

    def __repr__(self) -> str:
        return f"<BillStatusEvent id={self.id} {self.from_status}→{self.to_status}>"
