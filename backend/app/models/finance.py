"""Finance & COD Cash Handover models: CodHandover, CodHandoverItem, DepotLedger."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CodHandover(Base):
    """COD Cash Remittance Handover — maps to `cod_handovers` table."""

    __tablename__ = "cod_handovers"

    __table_args__ = (
        CheckConstraint(
            "total_cod_amount >= 0", name="ck_cod_handovers_total_amount",
        ),
        CheckConstraint(
            "actual_received_amount IS NULL OR actual_received_amount >= 0",
            name="ck_cod_handovers_actual_amount",
        ),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_cod_handovers_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    shipper_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    cashier_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    total_cod_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    actual_received_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    shipper: Mapped["User"] = relationship("User", foreign_keys=[shipper_id])
    cashier: Mapped["User | None"] = relationship("User", foreign_keys=[cashier_id])
    items: Mapped[list["CodHandoverItem"]] = relationship(
        "CodHandoverItem", back_populates="handover", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CodHandover id={self.id} code={self.code} status={self.status}>"


class CodHandoverItem(Base):
    """Line item bill in COD Handover — maps to `cod_handover_items` table."""

    __tablename__ = "cod_handover_items"

    handover_id: Mapped[int] = mapped_column(
        ForeignKey("cod_handovers.id", ondelete="CASCADE"), primary_key=True,
    )
    bill_id: Mapped[int] = mapped_column(
        ForeignKey("bills.id", ondelete="CASCADE"), primary_key=True, unique=True,
    )

    handover: Mapped["CodHandover"] = relationship("CodHandover", back_populates="items")
    bill: Mapped["Bill"] = relationship("Bill")

    def __repr__(self) -> str:
        return f"<CodHandoverItem handover_id={self.handover_id} bill_id={self.bill_id}>"


class DepotLedger(Base):
    """Depot Cash Vault Ledger Transaction — maps to `depot_ledgers` table."""

    __tablename__ = "depot_ledgers"

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('cod_collection', 'cod_payout', 'shipper_remittance', 'deposit', 'expense')",
            name="ck_depot_ledgers_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    reference_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )

    depot: Mapped["Depot"] = relationship("Depot")
    authorizer: Mapped["User"] = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<DepotLedger id={self.id} depot_id={self.depot_id} amount={self.amount}>"
