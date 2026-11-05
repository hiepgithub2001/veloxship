"""add import_batches and import_rows

Audit trail for the Excel importer: one batch per uploaded workbook and one row
per spreadsheet line, holding the raw cells, the normalised payload and the
validation verdict. Business tables (``bills``/``customers``) are untouched
until the batch is committed.

Revision ID: 0021
Revises: 0020
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(20), nullable=False),
        sa.Column("file_name", sa.Text, nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("source_layout", sa.String(32), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "total_rows", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column("ok_rows", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column(
            "warning_rows", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "error_rows", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "imported_rows", sa.Integer, nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "warnings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "options",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "created_by", sa.BigInteger, sa.ForeignKey("users.id"), nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "entity_type IN ('bill')", name="entity_type"
        ),
        sa.CheckConstraint(
            "status IN ('validating', 'validated', 'committing', 'completed', "
            "'partially_completed', 'failed')",
            name="status",
        ),
    )
    op.create_index(
        "ix_import_batches_creator",
        "import_batches",
        ["created_by", "created_at"],
    )
    op.create_index("ix_import_batches_hash", "import_batches", ["file_hash"])

    op.create_table(
        "import_rows",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "batch_id",
            sa.BigInteger,
            sa.ForeignKey("import_batches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("row_number", sa.Integer, nullable=False),
        sa.Column(
            "raw_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "normalized_data",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("error_code", sa.String(64), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "warnings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("target_id", sa.BigInteger, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('ok', 'warning', 'error', 'imported', 'skipped')",
            name="status",
        ),
    )
    op.create_index(
        "ux_import_rows_batch_row",
        "import_rows",
        ["batch_id", "row_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_import_rows_batch_row", table_name="import_rows")
    op.drop_table("import_rows")
    op.drop_index("ix_import_batches_hash", table_name="import_batches")
    op.drop_index("ix_import_batches_creator", table_name="import_batches")
    op.drop_table("import_batches")
