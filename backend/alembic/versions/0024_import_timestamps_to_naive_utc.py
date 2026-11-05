"""store import tables' timestamps as naive UTC

Migration ``0021``/``0023`` created ``import_batches`` and ``import_rows`` with
``timestamp with time zone`` columns, while every other table in this database
(``bills.created_at``, ``bill_status_logs.created_at``, …) stores **naive UTC**
— see ``app/core/timeutils.py``. The models follow the repo convention (plain
``Mapped[datetime]`` → naive ``DateTime``), so writing an aware value raised
``asyncpg.DataError: can't subtract offset-naive and offset-aware datetimes``
when a batch was committed.

This migration aligns the three columns with the rest of the schema. Existing
values are reinterpreted in UTC so nothing shifts.

Revision ID: 0024
Revises: 0023
Create Date: 2026-11-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0024"
down_revision: str | None = "0023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COLUMNS = (
    ("import_batches", "created_at"),
    ("import_batches", "committed_at"),
    ("import_rows", "created_at"),
)


def upgrade() -> None:
    for table, column in _COLUMNS:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {column} "
            f"TYPE timestamp without time zone "
            f"USING {column} AT TIME ZONE 'UTC'"
        )


def downgrade() -> None:
    for table, column in _COLUMNS:
        op.execute(
            f"ALTER TABLE {table} ALTER COLUMN {column} "
            f"TYPE timestamp with time zone "
            f"USING {column} AT TIME ZONE 'UTC'"
        )
