"""add customers_created to import_batches

The counter was first added directly to migration ``0021``. That is wrong once a
database has already applied it: ``alembic upgrade`` skips applied revisions, so
existing environments never got the column and every ``INSERT INTO import_batches``
failed with ``UndefinedColumnError`` (surfacing in the UI as a generic 500).
``0021`` is restored to its applied shape and the column ships here instead.

Revision ID: 0023
Revises: 0022
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0023"
down_revision: str | None = "0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "import_batches",
        sa.Column(
            "customers_created",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )


def downgrade() -> None:
    op.drop_column("import_batches", "customers_created")
