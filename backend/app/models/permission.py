"""Permission models: PermissionGroup, UserPermissionGroup, PermissionAction."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PermissionGroup(Base):
    """Permission Group — maps to `permission_groups` table."""

    __tablename__ = "permission_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    actions: Mapped[list["PermissionAction"]] = relationship(
        "PermissionAction", back_populates="group", cascade="all, delete-orphan",
    )
    user_groups: Mapped[list["UserPermissionGroup"]] = relationship(
        "UserPermissionGroup", back_populates="group", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<PermissionGroup id={self.id} name={self.name}>"


class UserPermissionGroup(Base):
    """Mapping table between User and PermissionGroup — maps to `user_permission_groups` table."""

    __tablename__ = "user_permission_groups"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True,
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("permission_groups.id", ondelete="CASCADE"), primary_key=True,
    )

    group: Mapped["PermissionGroup"] = relationship(
        "PermissionGroup", back_populates="user_groups",
    )

    def __repr__(self) -> str:
        return f"<UserPermissionGroup user_id={self.user_id} group_id={self.group_id}>"


class PermissionAction(Base):
    """Permission Action bound to PermissionGroup — maps to `permission_actions` table."""

    __tablename__ = "permission_actions"

    group_id: Mapped[int] = mapped_column(
        ForeignKey("permission_groups.id", ondelete="CASCADE"), primary_key=True,
    )
    action: Mapped[str] = mapped_column(String, primary_key=True)

    group: Mapped["PermissionGroup"] = relationship(
        "PermissionGroup", back_populates="actions",
    )

    def __repr__(self) -> str:
        return f"<PermissionAction group_id={self.group_id} action={self.action}>"
