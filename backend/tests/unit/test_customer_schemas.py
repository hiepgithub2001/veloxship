"""Unit tests for customer schemas — partial update, address flattening, money."""

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.customer import (
    CustomerCreate,
    CustomerMetrics,
    CustomerRead,
    CustomerUpdate,
)


def _customer_read(**overrides) -> CustomerRead:
    """Build a CustomerRead from ORM-like kwargs."""
    payload = {
        "id": 1,
        "code": "KH000001",
        "name": "Cửa hàng Hà Nội",
        "phone": "0901000001",
        "customer_type": "shop",
        "customer_metadata": None,
        "is_active": True,
        "created_at": datetime(2026, 10, 1, 8, 0, 0),
        "updated_at": datetime(2026, 10, 1, 8, 0, 0),
    }
    payload.update(overrides)
    return CustomerRead.model_validate(payload)


class TestCustomerCreate:
    """Validation on the manual-create payload."""

    def test_defaults_to_retail(self):
        schema = CustomerCreate(name="Khách lẻ")
        assert schema.customer_type == "retail"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            CustomerCreate(name="")

    def test_unknown_customer_type_rejected(self):
        with pytest.raises(ValidationError):
            CustomerCreate(name="Khách", customer_type="vip")

    @pytest.mark.parametrize("customer_type", ["retail", "shop", "enterprise"])
    def test_accepts_known_customer_types(self, customer_type):
        schema = CustomerCreate(name="Khách", customer_type=customer_type)
        assert schema.customer_type == customer_type


class TestCustomerUpdate:
    """Partial-update semantics: only explicitly-set fields are returned."""

    def test_exclude_unset_returns_only_provided_fields(self):
        schema = CustomerUpdate(name="Tên mới")
        assert schema.model_dump(exclude_unset=True) == {"name": "Tên mới"}

    def test_explicit_none_is_kept(self):
        schema = CustomerUpdate(phone=None)
        assert schema.model_dump(exclude_unset=True) == {"phone": None}

    def test_is_active_toggle(self):
        schema = CustomerUpdate(is_active=False)
        assert schema.model_dump(exclude_unset=True) == {"is_active": False}

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            CustomerUpdate(name="")

    def test_unknown_customer_type_rejected(self):
        with pytest.raises(ValidationError):
            CustomerUpdate(customer_type="vip")


class TestCustomerReadFlattening:
    """Address lives in `metadata` but is exposed flattened for the edit form."""

    def test_address_fields_copied_from_metadata(self):
        customer = _customer_read(
            customer_metadata={
                "address_detail": "1 Phố Huế",
                "province_code": "01",
                "province_name": "Hà Nội",
                "ward_code": "00001",
                "ward_name": "Phúc Tân",
            }
        )
        assert customer.address_detail == "1 Phố Huế"
        assert customer.province_code == "01"
        assert customer.province_name == "Hà Nội"
        assert customer.ward_code == "00001"
        assert customer.ward_name == "Phúc Tân"

    def test_metadata_still_exposed(self):
        customer = _customer_read(customer_metadata={"province_name": "Hà Nội"})
        assert customer.metadata == {"province_name": "Hà Nội"}

    def test_missing_metadata_leaves_fields_none(self):
        customer = _customer_read()
        assert customer.metadata is None
        assert customer.address_detail is None
        assert customer.province_name is None

    def test_explicit_value_wins_over_metadata(self):
        customer = _customer_read(
            customer_metadata={"province_name": "Hà Nội"},
            province_name="Đà Nẵng",
        )
        assert customer.province_name == "Đà Nẵng"


class TestCustomerMetrics:
    """Money is Decimal and must serialize as a string, not a float."""

    def test_total_revenue_is_decimal(self):
        metrics = CustomerMetrics(
            total_bills=3,
            total_revenue=Decimal("1500000.50"),
            delivered_bills=2,
            cancelled_bills=0,
        )
        assert metrics.total_revenue == Decimal("1500000.50")

    def test_total_revenue_serializes_as_string(self):
        metrics = CustomerMetrics(
            total_bills=1,
            total_revenue=Decimal("999.99"),
            delivered_bills=1,
            cancelled_bills=0,
        )
        assert '"total_revenue":"999.99"' in metrics.model_dump_json()

    def test_optional_dates_default_to_none(self):
        metrics = CustomerMetrics(
            total_bills=0,
            total_revenue=Decimal("0"),
            delivered_bills=0,
            cancelled_bills=0,
        )
        assert metrics.first_bill_at is None
        assert metrics.last_bill_at is None
