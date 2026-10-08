"""User (Nhân viên) model."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.depot import Depot
    from app.models.permission import Role


class User(Base):
    """Staff user account — maps to `users` table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(
        Text, ForeignKey("roles.code"), nullable=False, default="operator",
    )
    user_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSONB, nullable=True,
    )
    depot_id: Mapped[int | None] = mapped_column(
        ForeignKey("depots.id"), nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now(),
    )

    depot: Mapped["Depot | None"] = relationship("Depot", back_populates="users")
    role_ref: Mapped["Role | None"] = relationship("Role")

    @property
    def department(self) -> str | None:
        return (self.user_metadata or {}).get("department")

    @property
    def position(self) -> str | None:
        return (self.user_metadata or {}).get("position")

    @property
    def employee_code(self) -> str | None:
        return (self.user_metadata or {}).get("employee_code")

    @property
    def role_name(self) -> str | None:
        return self.role_ref.name if self.role_ref else None

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username} role={self.role}>"
