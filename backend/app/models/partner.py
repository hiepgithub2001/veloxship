"""Partner and PartnerTariff models (Đối tác 3PL & Cước phí mua)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Partner(Base):
    """3PL Partner Carrier — maps to `partners` table."""

    __tablename__ = "partners"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    api_url: Mapped[str] = mapped_column(Text, nullable=False)
    api_token: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    tariffs: Mapped[list["PartnerTariff"]] = relationship(
        "PartnerTariff", back_populates="partner", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Partner id={self.id} code={self.code} name={self.name}>"


class PartnerTariff(Base):
    """3PL Partner Cost Tariff line — maps to `partner_tariffs` table."""

    __tablename__ = "partner_tariffs"

    __table_args__ = (
        CheckConstraint("base_fee >= 0", name="ck_partner_tariffs_base_fee"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    partner_id: Mapped[int] = mapped_column(
        ForeignKey("partners.id", ondelete="CASCADE"), nullable=False,
    )
    service_name: Mapped[str] = mapped_column(Text, nullable=False)
    route_type: Mapped[str] = mapped_column(Text, nullable=False)
    base_fee: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00"),
    )

    partner: Mapped["Partner"] = relationship("Partner", back_populates="tariffs")

    def __repr__(self) -> str:
        return f"<PartnerTariff id={self.id} partner_id={self.partner_id} service={self.service_name}>"
