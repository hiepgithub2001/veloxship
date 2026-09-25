"""add customer code sequence and backfill existing customers

Revision ID: 0014
Revises: 0013
"""

from typing import Sequence, Union

from alembic import op

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS customer_code_seq START 1 CACHE 50")
    # Backfill existing customers with a deterministic code derived from their id,
    # then advance the sequence past the highest id so future codes never collide.
    op.execute(
        "UPDATE customers SET code = 'KH' || lpad(id::text, 6, '0') WHERE code IS NULL"
    )
    op.execute(
        "SELECT setval('customer_code_seq', GREATEST((SELECT COALESCE(MAX(id), 0) FROM customers) + 1, 1), false)"
    )


def downgrade() -> None:
    op.execute("DROP SEQUENCE IF EXISTS customer_code_seq")
