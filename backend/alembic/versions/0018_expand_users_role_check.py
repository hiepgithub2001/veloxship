"""expand users.role check constraint to the six current roles

Revision ID: 0018
Revises: 0017
Create Date: 2026-10-08

The `users` table was originally created (0002) with the legacy role enum
`('staff', 'supervisor', 'admin')`. The IAM/RBAC work later moved to six roles
(`shipper`, `depot_manager`, `cashier`, `accountant`, `operator`, `admin`) in
the model, but no migration updated the DB check constraint, so inserting a
user with any of the new roles (e.g. `shipper`) raised a CheckViolationError.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: Union[str, None] = "0017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CONSTRAINT_NAME = "ck_users_ck_users_role"

NEW_ROLES = (
    "shipper",
    "depot_manager",
    "cashier",
    "accountant",
    "operator",
    "admin",
)

OLD_ROLES = ("staff", "supervisor", "admin")


def upgrade() -> None:
    op.drop_constraint(op.f(CONSTRAINT_NAME), "users", type_="check")
    op.create_check_constraint(
        op.f(CONSTRAINT_NAME),
        "users",
        "role IN ('shipper', 'depot_manager', 'cashier', 'accountant', 'operator', 'admin')",
    )


def downgrade() -> None:
    op.drop_constraint(op.f(CONSTRAINT_NAME), "users", type_="check")
    op.create_check_constraint(
        op.f(CONSTRAINT_NAME),
        "users",
        "role IN ('staff', 'supervisor', 'admin')",
    )
