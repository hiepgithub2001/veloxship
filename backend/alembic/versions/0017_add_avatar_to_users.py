"""add avatar column to users

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-08

Adds a nullable `avatar` column to `users` for the self-service account
(profile) module. The column stores an S3 object key; the API presigns it
into a temporary URL when reading the current user.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("avatar", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "avatar")
