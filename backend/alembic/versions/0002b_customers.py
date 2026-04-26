"""Create customers table (required by bills FK).

Revision ID: 0002b
Revises: 0002
Create Date: 2026-04-26
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002b"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("customer_code", sa.Text, unique=True, nullable=False),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("district", sa.Text, nullable=True),
        sa.Column("province", sa.Text, nullable=True),
        sa.Column("phone", sa.Text, nullable=True),
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
    )
    # Create immutable wrapper for unaccent
    op.execute("""
        CREATE OR REPLACE FUNCTION f_unaccent(text)
        RETURNS text AS $$
        SELECT public.unaccent('public.unaccent', $1)
        $$ LANGUAGE sql IMMUTABLE STRICT;
    """)

    # GIN trigram index for search
    op.execute(
        "CREATE INDEX idx_customers_search_name ON customers "
        "USING GIN (f_unaccent(lower(display_name)) gin_trgm_ops)"
    )
    op.create_index("idx_customers_phone", "customers", ["phone"])


def downgrade() -> None:
    op.drop_index("idx_customers_phone", table_name="customers")
    op.drop_index("idx_customers_search_name", table_name="customers")
    op.drop_table("customers")
