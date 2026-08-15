"""Ward (Phường/Xã) model."""

from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ward(Base):
    """Administrative division: Ward — maps to `wards` table."""

    __tablename__ = "wards"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    name_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    province_code: Mapped[str] = mapped_column(
        String, ForeignKey("provinces.code"), nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )

    province: Mapped["Province"] = relationship("Province", back_populates="wards", lazy="joined")

    def __repr__(self) -> str:
        return f"<Ward code={self.code} name={self.name}>"
