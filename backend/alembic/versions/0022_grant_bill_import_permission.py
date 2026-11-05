"""grant bill:import to operator and depot_manager

The action is added to ``PERMISSION_CATALOG`` in code, but permissions are
**rows** in ``role_permissions`` (migration 0019), so existing deployments need
this migration to actually hand the action to the roles that run imports.
``admin`` bypasses every check and needs no row.

Revision ID: 0022
Revises: 0021
Create Date: 2026-11-05
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ACTION = "bill:import"
TARGET_ROLES = ("operator", "depot_manager")


def upgrade() -> None:
    for role in TARGET_ROLES:
        op.execute(
            sa.text(
                "INSERT INTO role_permissions (role, action) VALUES (:role, :action) "
                "ON CONFLICT DO NOTHING"
            ).bindparams(role=role, action=ACTION)
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM role_permissions WHERE action = :action AND role IN "
            "('operator', 'depot_manager')"
        ).bindparams(action=ACTION)
    )
