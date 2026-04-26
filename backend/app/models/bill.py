"""Bill (Phiếu Gửi) model."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Bill(Base):
    """Delivery bill — maps to `bills` table."""

    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tracking_number: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    # Customer link (optional)
    customer_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("customers.id"), nullable=True,
    )

    # Sender snapshot
    sender_name: Mapped[str] = mapped_column(Text, nullable=False)
    sender_address: Mapped[str] = mapped_column(Text, nullable=False)
    sender_district: Mapped[str] = mapped_column(Text, nullable=False)
    sender_province: Mapped[str] = mapped_column(Text, nullable=False)
    sender_phone: Mapped[str] = mapped_column(Text, nullable=False)

    # Receiver snapshot
    receiver_name: Mapped[str] = mapped_column(Text, nullable=False)
    receiver_address: Mapped[str] = mapped_column(Text, nullable=False)
    receiver_district: Mapped[str] = mapped_column(Text, nullable=False)
    receiver_province: Mapped[str] = mapped_column(Text, nullable=False)
    receiver_phone: Mapped[str] = mapped_column(Text, nullable=False)

    # Service
    cargo_type: Mapped[str] = mapped_column(String, nullable=False)
    service_tier_code: Mapped[str] = mapped_column(
        String, ForeignKey("service_tiers.code"), nullable=False,
    )

    # Fees (VND)
    fee_main: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fee_fuel_surcharge: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fee_other_surcharge: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fee_vat: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fee_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    # Payer
    payer: Mapped[str] = mapped_column(String, nullable=False)

    # Lifecycle
    status: Mapped[str] = mapped_column(String, nullable=False, default="da_tao")
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_to_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )
    print_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_printed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_printed_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True,
    )

    # Relationships
    content_lines = relationship("BillContentLine", back_populates="bill", cascade="all, delete-orphan", order_by="BillContentLine.line_no")
    status_events = relationship("BillStatusEvent", back_populates="bill", cascade="all, delete-orphan", order_by="BillStatusEvent.created_at")

    def __repr__(self) -> str:
        return f"<Bill id={self.id} tracking={self.tracking_number}>"
