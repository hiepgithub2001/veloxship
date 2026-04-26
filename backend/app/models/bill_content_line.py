"""Bill content line model."""

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BillContentLine(Base):
    """Content line for a bill — maps to `bill_content_lines` table."""

    __tablename__ = "bill_content_lines"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    bill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False,
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    length_cm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    width_cm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)

    bill = relationship("Bill", back_populates="content_lines")

    def __repr__(self) -> str:
        return f"<BillContentLine id={self.id} bill_id={self.bill_id} line_no={self.line_no}>"
