"""add indexes for global bill search

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-08
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_customers_search_name_unaccent ON customers "
            "USING GIN (f_unaccent(lower(name)) gin_trgm_ops)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_customers_search_phone_trgm ON customers "
            "USING GIN (phone gin_trgm_ops)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY idx_bills_search_tracking_unaccent ON bills "
            "USING GIN (f_unaccent(lower(tracking_number)) gin_trgm_ops)"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_bills_search_tracking_unaccent")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_customers_search_phone_trgm")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_customers_search_name_unaccent")
