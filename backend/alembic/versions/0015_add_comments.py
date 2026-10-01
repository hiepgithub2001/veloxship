"""add comments table

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("entity_id", sa.BigInteger, nullable=False),
        sa.Column(
            "author_id",
            sa.BigInteger,
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column(
            "images",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "parent_id",
            sa.BigInteger,
            sa.ForeignKey("comments.id", ondelete="CASCADE"),
            nullable=True,
        ),
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
            "entity_type IN ('bill', 'customer', 'depot', 'vehicle')",
            name="ck_comments_entity_type",
        ),
    )
    op.create_index(
        "ix_comments_entity",
        "comments",
        ["entity_type", "entity_id", "is_active", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_comments_entity", table_name="comments")
    op.drop_table("comments")
