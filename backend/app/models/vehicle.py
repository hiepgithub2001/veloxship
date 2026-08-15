"""Vehicle (Đội xe kho hàng) model."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Vehicle(Base):
    """Vehicle fleet — maps to `vehicles` table."""

    __tablename__ = "vehicles"

    __table_args__ = (
        CheckConstraint(
            "vehicle_type IN ('motorcycle', 'truck')", name="ck_vehicles_type",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'maintenance')", name="ck_vehicles_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    license_plate: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String, nullable=False)
    max_weight_kg: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    max_volume_m3: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    latest_depot_id: Mapped[int | None] = mapped_column(
        ForeignKey("depots.id"), nullable=True,
    )
    latest_linehaul_id: Mapped[int | None] = mapped_column(
        ForeignKey("linehauls.id", use_alter=True, name="fk_vehicles_latest_linehaul_id"), nullable=True,
    )
    driver_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True,
    )
    images: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]",
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    latest_depot: Mapped["Depot | None"] = relationship("Depot", foreign_keys=[latest_depot_id], lazy="joined")
    latest_linehaul: Mapped["Linehaul | None"] = relationship("Linehaul", foreign_keys=[latest_linehaul_id])
    driver: Mapped["User | None"] = relationship("User", foreign_keys=[driver_id], lazy="joined")

    @property
    def driver_name(self) -> str | None:
        return self.driver.full_name if self.driver else None

    @property
    def depot_name(self) -> str | None:
        return self.latest_depot.name if self.latest_depot else None

    def __repr__(self) -> str:
        return f"<Vehicle id={self.id} plate={self.license_plate} type={self.vehicle_type}>"
