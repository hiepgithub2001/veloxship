"""Province (Tỉnh/Thành phố) model."""

from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Province(Base):
    """Administrative division: Province / City — maps to `provinces` table."""

    __tablename__ = "provinces"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )

    wards: Mapped[list["Ward"]] = relationship(
        "Ward", back_populates="province", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Province code={self.code} name={self.name}>"
