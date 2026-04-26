"""Service tier (Dịch vụ) model."""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ServiceTier(Base):
    """Service tier catalogue — maps to `service_tiers` table."""

    __tablename__ = "service_tiers"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(
        String, nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<ServiceTier code={self.code}>"
