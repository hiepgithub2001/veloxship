"""Permission action catalogue and helpers.

The catalogue drives the permission-management UI (UC-WEB-10). It groups
the assignable `permission_actions.action` strings by business module. The
Vietnamese labels are kept server-side so the backend remains the single
source of truth for the "which actions exist" list.
"""

from __future__ import annotations

# Each module maps to a list of {code, label} actions. The `code` values are
# the strings persisted in `permission_actions.action` and enforced by
# `require_permission`.
PERMISSION_CATALOG: list[dict] = [
    {
        "code": "bill",
        "label": "Phân hệ Vận đơn",
        "actions": [
            {"code": "bill:view", "label": "Xem vận đơn"},
            {"code": "bill:create", "label": "Tạo vận đơn"},
            {"code": "bill:update", "label": "Cập nhật vận đơn"},
            {"code": "bill:cancel", "label": "Hủy vận đơn"},
            {"code": "bill:rollback", "label": "Hủy giao hàng thành công"},
            {"code": "bill:adjust_cod", "label": "Điều chỉnh COD"},
        ],
    },
    {
        "code": "warehouse",
        "label": "Phân hệ Kho hàng",
        "actions": [
            {"code": "warehouse:inbound", "label": "Nhập kho"},
            {"code": "warehouse:outbound", "label": "Xuất kho giao hàng"},
            {"code": "warehouse:bagging", "label": "Đóng bao trung chuyển"},
            {"code": "warehouse:audit", "label": "Kiểm điểm kho"},
        ],
    },
    {
        "code": "customer",
        "label": "Phân hệ Khách hàng",
        "actions": [
            {"code": "customer:view", "label": "Xem khách hàng"},
            {"code": "customer:create", "label": "Tạo khách hàng"},
            {"code": "customer:update", "label": "Cập nhật khách hàng"},
            {"code": "customer:delete", "label": "Xóa khách hàng"},
        ],
    },
    {
        "code": "finance",
        "label": "Phân hệ Tài chính / COD",
        "actions": [
            {"code": "finance:cod_handover", "label": "Lập bảng kê COD"},
            {"code": "finance:cashier_confirm", "label": "Xác nhận thu tiền"},
            {"code": "finance:ledger", "label": "Sổ quỹ kho"},
        ],
    },
    {
        "code": "fleet",
        "label": "Phân hệ Đội xe",
        "actions": [
            {"code": "fleet:view", "label": "Xem đội xe"},
            {"code": "fleet:manage", "label": "Quản lý đội xe"},
        ],
    },
    {
        "code": "depot",
        "label": "Phân hệ Bưu cục / Kho",
        "actions": [
            {"code": "depot:view", "label": "Xem bưu cục"},
            {"code": "depot:manage", "label": "Quản lý bưu cục"},
        ],
    },
    {
        "code": "iam",
        "label": "Quản trị hệ thống",
        "actions": [
            {"code": "iam:view_users", "label": "Xem nhân viên"},
            {"code": "iam:manage_users", "label": "Quản lý nhân viên"},
            {"code": "iam:manage_permissions", "label": "Quản lý phân quyền"},
        ],
    },
]


def valid_action_codes() -> set[str]:
    """Return the flat set of every assignable action code."""
    return {
        action["code"] for module in PERMISSION_CATALOG for action in module["actions"]
    }


def is_valid_action(action: str) -> bool:
    """Return True when `action` belongs to the catalogue."""
    return action in valid_action_codes()


# Stable role codes → Vietnamese labels. Roles are DYNAMIC: these six are only
# the default seed — admins may add, rename (the label) or delete other roles.
ROLE_LABELS: dict[str, str] = {
    "admin": "Quản trị viên",
    "operator": "Nhân viên quầy",
    "depot_manager": "Thủ kho",
    "cashier": "Thủ quỹ",
    "accountant": "Kế toán",
    "shipper": "Bưu tá",
}

# Reserved role code that bypasses every permission check.
ADMIN_ROLE = "admin"

# Default action grants per role — used only to seed `role_permissions`.
ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    "admin": sorted(valid_action_codes()),
    "operator": [
        "bill:view", "bill:create", "bill:update",
        "customer:view", "customer:create", "customer:update",
        "warehouse:inbound", "warehouse:outbound",
    ],
    "depot_manager": [
        "bill:view",
        "customer:view",
        "warehouse:inbound", "warehouse:outbound",
        "warehouse:bagging", "warehouse:audit",
    ],
    "cashier": [
        "bill:view",
        "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
    ],
    "accountant": [
        "bill:view", "customer:view",
        "finance:cod_handover", "finance:cashier_confirm", "finance:ledger",
    ],
    "shipper": ["bill:view", "warehouse:outbound"],
}


def default_roles() -> list[dict]:
    """Return the default role seed (code + Vietnamese label)."""
    return [
        {"code": code, "name": label}
        for code, label in ROLE_LABELS.items()
    ]
