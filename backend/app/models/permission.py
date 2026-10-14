"""Role and role-permission models.

A role is a dynamic record (seeded with six defaults); each role maps directly
to a set of permission actions via `role_permissions`. There is no separate
"permission group" indirection anymore.
"""

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    """User role — maps to `roles` table."""

    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    permissions: Mapped[list["RolePermission"]] = relationship(
        "RolePermission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Role code={self.code} name={self.name}>"


class RolePermission(Base):
    """Role → action mapping — maps to `role_permissions` table."""

    __tablename__ = "role_permissions"

    role: Mapped[str] = mapped_column(
        Text, ForeignKey("roles.code", ondelete="CASCADE"), primary_key=True,
    )
    action: Mapped[str] = mapped_column(String, primary_key=True)

    def __repr__(self) -> str:
        return f"<RolePermission role={self.role} action={self.action}>"
