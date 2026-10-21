"""add indexes on bills(sender_id) and bills(receiver_id)

The customer module reads a customer's bill history and activity metrics by
filtering `bills` on `sender_id` / `receiver_id`. PostgreSQL does not create
indexes for foreign keys automatically, so both columns were sequential-scan
only. These indexes keep the customer detail page fast as `bills` grows.

Index-only change: no table or data modification.

Revision ID: 0020
Revises: 0019
Create Date: 2026-10-15
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # CONCURRENTLY cannot run inside a transaction, hence the autocommit block.
    with op.get_context().autocommit_block():
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bills_sender_id "
            "ON bills (sender_id)"
        )
        op.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bills_receiver_id "
            "ON bills (receiver_id)"
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_bills_receiver_id")
        op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_bills_sender_id")
