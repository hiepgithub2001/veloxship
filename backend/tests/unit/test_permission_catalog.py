"""Unit tests for the permission action catalogue."""

from app.core.permissions import (
    PERMISSION_CATALOG,
    ROLE_DEFAULT_PERMISSIONS,
    is_valid_action,
    valid_action_codes,
)


class TestPermissionCatalog:
    """Test the assignable action catalogue integrity."""

    def test_catalog_is_non_empty(self):
        assert len(PERMISSION_CATALOG) > 0

    def test_every_module_has_label_and_actions(self):
        for module in PERMISSION_CATALOG:
            assert module["code"]
            assert module["label"]
            assert module["actions"], f"module {module['code']} has no actions"

    def test_action_codes_are_unique_across_modules(self):
        codes = valid_action_codes()
        total = sum(len(m["actions"]) for m in PERMISSION_CATALOG)
        assert len(codes) == total, "duplicate action codes detected"

    def test_is_valid_action(self):
        assert is_valid_action("bill:create") is True
        assert is_valid_action("iam:manage_users") is True
        assert is_valid_action("nonexistent:action") is False

    def test_dashboard_view_is_registered_and_granted(self):
        assert is_valid_action("dashboard:view") is True
        # Admin bypasses checks (auto-holds every action via sorted set).
        assert "dashboard:view" in ROLE_DEFAULT_PERMISSIONS["admin"]
        # Desk roles hold it; the field courier does not.
        for role in ("operator", "depot_manager", "cashier", "accountant"):
            assert "dashboard:view" in ROLE_DEFAULT_PERMISSIONS[role]
        assert "dashboard:view" not in ROLE_DEFAULT_PERMISSIONS["shipper"]

