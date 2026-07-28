"""Bill (Phiếu Gửi / Vận Đơn) model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Bill(Base):
    """Delivery bill — maps to `bills` table."""

    __tablename__ = "bills"

    __table_args__ = (
        CheckConstraint(
            "cargo_type IN ('document', 'goods')", name="ck_bills_cargo_type",
        ),
        CheckConstraint(
            "payer IN ('sender', 'receiver')", name="ck_bills_payer",
        ),
        CheckConstraint(
            "status IN ('created', 'picked_up', 'in_transit', 'delivered', 'returned', 'cancelled')",
            name="ck_bills_status",
        ),
        CheckConstraint(
            "fee_total = fee_main + fee_insurance + fee_other + fee_vat",
            name="ck_bills_fee_total",
        ),
        CheckConstraint(
            "status <> 'cancelled' OR cancellation_reason IS NOT NULL",
            name="ck_bills_cancel_reason",
        ),
        CheckConstraint(
            "status <> 'delivered' OR (delivered_at IS NOT NULL AND delivered_to_name IS NOT NULL)",
            name="ck_bills_delivered",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tracking_number: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    # Customers (FKs)
    sender_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    # Service & Cargo
    cargo_type: Mapped[str] = mapped_column(String, nullable=False)
    service_tier_code: Mapped[str] = mapped_column(
        String, ForeignKey("service_tiers.code"), nullable=False,
    )
    actual_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0.000"))
    chargeable_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False, default=Decimal("0.000"))
    is_insurance_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cod_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))

    # Fees (VND)
    fee_main: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    fee_insurance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    fee_other: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    fee_vat: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0.00"))
    fee_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    # Payer
    payer: Mapped[str] = mapped_column(String, nullable=False)

    # Routing & Staff
    origin_depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"), nullable=True)
    destination_depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"), nullable=True)
    latest_depot_id: Mapped[int | None] = mapped_column(ForeignKey("depots.id"), nullable=True)
    latest_linehaul_id: Mapped[int | None] = mapped_column(
        ForeignKey("linehauls.id", use_alter=True, name="fk_bills_latest_linehaul_id"), nullable=True,
    )
    shipper_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    partner_id: Mapped[int | None] = mapped_column(ForeignKey("partners.id"), nullable=True)
    partner_bill_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(String, nullable=False, default="created")
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
    sender: Mapped["Customer"] = relationship("Customer", foreign_keys=[sender_id])
    receiver: Mapped["Customer"] = relationship("Customer", foreign_keys=[receiver_id])
    origin_depot: Mapped["Depot | None"] = relationship("Depot", foreign_keys=[origin_depot_id])
    destination_depot: Mapped["Depot | None"] = relationship("Depot", foreign_keys=[destination_depot_id])
    latest_depot: Mapped["Depot | None"] = relationship("Depot", foreign_keys=[latest_depot_id])
    latest_linehaul: Mapped["Linehaul | None"] = relationship("Linehaul", foreign_keys=[latest_linehaul_id])
    shipper: Mapped["User | None"] = relationship("User", foreign_keys=[shipper_id])
    partner: Mapped["Partner | None"] = relationship("Partner", foreign_keys=[partner_id])

    content_lines = relationship("BillContentLine", back_populates="bill", cascade="all, delete-orphan", order_by="BillContentLine.line_no")
    status_logs = relationship("BillStatusLog", back_populates="bill", cascade="all, delete-orphan", order_by="BillStatusLog.created_at")

    def __repr__(self) -> str:
        return f"<Bill id={self.id} tracking={self.tracking_number} status={self.status}>"
