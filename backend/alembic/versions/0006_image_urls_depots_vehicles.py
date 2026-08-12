"""add image_urls JSON column to depots and vehicles

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-12 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("depots", sa.Column("image_urls", JSON(none_as_null=True), nullable=True))
    op.add_column("vehicles", sa.Column("image_urls", JSON(none_as_null=True), nullable=True))


def downgrade() -> None:
    op.drop_column("vehicles", "image_urls")
    op.drop_column("depots", "image_urls")
