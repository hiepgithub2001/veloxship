"""Comment model — bình luận gắn vào nhiều đối tượng (polymorphic)."""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Comment(Base):
    """Comment thread — maps to `comments` table.

    Attaches to multiple entity types via `entity_type` + `entity_id`
    (polymorphic, no FK to a single table). Replies are limited to one level
    via `parent_id`.
    """

    __tablename__ = "comments"

    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('bill', 'customer', 'depot', 'vehicle')",
            name="ck_comments_entity_type",
        ),
        Index("ix_comments_entity", "entity_type", "entity_id", "is_active", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    images: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    author = relationship("User", foreign_keys=[author_id])
    replies = relationship("Comment", back_populates="parent")
    parent = relationship("Comment", back_populates="replies", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Comment id={self.id} {self.entity_type}#{self.entity_id}>"
