"""Linehaul (Chuyến xe trung chuyển) model."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Linehaul(Base):
    """Linehaul transit trip — maps to `linehauls` table."""

    __tablename__ = "linehauls"

    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'loading', 'in_transit', 'arrived', 'completed')",
            name="ck_linehauls_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    origin_depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False)
    destination_depot_id: Mapped[int] = mapped_column(ForeignKey("depots.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled")
    start_odometer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_odometer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", foreign_keys=[vehicle_id])
    driver: Mapped["User"] = relationship("User", foreign_keys=[driver_id])
    origin_depot: Mapped["Depot"] = relationship("Depot", foreign_keys=[origin_depot_id])
    destination_depot: Mapped["Depot"] = relationship("Depot", foreign_keys=[destination_depot_id])

    def __repr__(self) -> str:
        return f"<Linehaul id={self.id} code={self.code} status={self.status}>"
