"""Depot (Kho hàng / Bưu cục) model."""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Depot(Base):
    """Depot / Warehouse / Post Office — maps to `depots` table."""

    __tablename__ = "depots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str] = mapped_column(Text, nullable=False)
    address_detail: Mapped[str] = mapped_column(Text, nullable=False)
    ward_code: Mapped[str | None] = mapped_column(
        String, ForeignKey("wards.code"), nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
 image_urls: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    ward: Mapped["Ward | None"] = relationship("Ward")
    users: Mapped[list["User"]] = relationship("User", back_populates="depot")

    def __repr__(self) -> str:
        return f"<Depot id={self.id} code={self.code} name={self.name}>"
