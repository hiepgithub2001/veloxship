"""Create users, service_tiers, audit_events tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("username", sa.Text, unique=True, nullable=False),
        sa.Column("full_name", sa.Text, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False, server_default="staff"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "role IN ('staff', 'supervisor', 'admin')",
            name="ck_users_role",
        ),
    )

    # --- service_tiers ---
    op.create_table(
        "service_tiers",
        sa.Column("code", sa.Text, primary_key=True),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("scope", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.CheckConstraint(
            "scope IN ('domestic', 'international')",
            name="ck_service_tiers_scope",
        ),
    )

    # Seed service tiers
    op.execute("""
        INSERT INTO service_tiers (code, display_name, scope) VALUES
        ('CPN', 'Chuyển phát nhanh', 'domestic'),
        ('PHT', 'Phát hỏa tốc', 'domestic'),
        ('DUONG_BO', 'Đường bộ', 'domestic'),
        ('T48H', 'Tiết kiệm 48h', 'domestic'),
        ('NGUYEN_CHUYEN', 'Nguyên chuyến', 'domestic'),
        ('KHAC', 'Khác', 'domestic'),
        ('INTL_EXPRESS', 'Quốc tế nhanh', 'international'),
        ('INTL_ECONOMY', 'Quốc tế tiết kiệm', 'international'),
        ('INTL_OTHER', 'Quốc tế khác', 'international')
    """)

    # --- audit_events ---
    op.create_table(
        "audit_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("actor_id", sa.BigInteger, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column("entity_type", sa.Text, nullable=True),
        sa.Column("entity_id", sa.BigInteger, nullable=True),
        sa.Column("details", JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "idx_audit_events_entity",
        "audit_events",
        ["entity_type", "entity_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_audit_events_entity", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("service_tiers")
    op.drop_table("users")
