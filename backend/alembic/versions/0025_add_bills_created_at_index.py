"""add index on bills(created_at)

The dashboard aggregates bills by creation-date range (`bills.created_at >= ...
AND < ...`). The existing `idx_bills_status_created_at` is keyed on `status`
first, so it does not serve a range-only filter, and PostgreSQL does not create
an index for the column automatically. This index keeps the dashboard queries a
range scan instead of a full table scan as `bills` grows.

Index-only change: no table or data modification.

Revision ID: 0025
Revises: 0024
Create Date: 2026-11-06
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0025"
down_revision: str | None = "0024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # CONCURRENTLY cannot run inside a transaction, hence the autocommit block.
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bills_created_at "
            "ON bills (created_at)"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_bills_created_at")
