"""Bill status log model (lịch sử hành trình vận đơn)."""

from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BillStatusLog(Base):
    """Status change history — maps to `bill_status_logs` table."""

    __tablename__ = "bill_status_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False,
    )
    from_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    to_status: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    latest_linehaul_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("linehauls.id", use_alter=True, name="fk_bill_status_events_latest_linehaul_id"), nullable=True,
    )
    latest_depot_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("depots.id"), nullable=True,
    )
    changed_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    bill = relationship("Bill", back_populates="status_logs")
    latest_linehaul = relationship("Linehaul", foreign_keys=[latest_linehaul_id])
    latest_depot = relationship("Depot", foreign_keys=[latest_depot_id])
    user = relationship("User", foreign_keys=[changed_by])

    def __repr__(self) -> str:
        return f"<BillStatusLog id={self.id} {self.from_status}→{self.to_status}>"


# Alias for backward compatibility
BillStatusEvent = BillStatusLog
