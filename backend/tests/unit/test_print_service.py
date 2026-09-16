"""Unit tests for the canonical bill print context and template."""

from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace

from app.services.print_service import _prepare_context, render_bill_html


def _bill_fixture():
    customer = SimpleNamespace(
        code="KH001",
        name="Tên hồ sơ đã đổi",
        phone="0000000000",
        customer_metadata={},
    )
    line = SimpleNamespace(
        description="Tài liệu hợp đồng",
        quantity=2,
        weight_kg=Decimal("1.250"),
        length_cm=Decimal("20"),
        width_cm=Decimal("15.5"),
        height_cm=Decimal("10"),
    )
    return SimpleNamespace(
        tracking_number="NL00001",
        sender=customer,
        receiver=customer,
        sender_snapshot={
            "name": "Nguyễn Văn Gửi",
            "phone": "0901000001",
            "address_detail": "12 Lê Lợi",
            "ward_name": "Phường Bến Nghé",
            "province_name": "TP. Hồ Chí Minh",
        },
        receiver_snapshot={
            "name": "Trần Thị Nhận",
            "phone": "0901000002",
            "address_detail": "45 Nguyễn Huệ",
            "ward_name": "Phường Sài Gòn",
            "province_name": "TP. Hồ Chí Minh",
        },
        content_lines=[line],
        service_tier_code="CPN",
        service_tier=SimpleNamespace(scope="domestic"),
        actual_weight_kg=Decimal("1.250"),
        chargeable_weight_kg=Decimal("1.500"),
        cod_amount=Decimal("1500000"),
        fee_main=Decimal("25000"),
        fee_insurance=Decimal("5000"),
        fee_other=Decimal("1000"),
        fee_vat=Decimal("3100"),
        fee_total=Decimal("34100"),
        payer="sender",
        cargo_type="document",
        created_at=datetime(2026, 9, 16, 3, 0, tzinfo=UTC),
    )


def test_print_context_uses_snapshots_and_explicit_placeholders():
    context = _prepare_context(_bill_fixture())

    assert context["sender"]["name"] == "Nguyễn Văn Gửi"
    assert context["sender"]["name"] != "Tên hồ sơ đã đổi"
    assert context["sender"]["district_name"] == "—"
    assert context["fee_fuel_surcharge"] == "0"
    assert context["is_domestic"] is True
    assert context["is_international"] is False
    assert next(item for item in context["domestic_services"] if item["code"] == "CPN")[
        "checked"
    ]
    assert len(context["content_lines"]) == 5
    assert sum(line["is_blank"] for line in context["content_lines"]) == 4
    assert [copy["label"] for copy in context["copies"]] == [
        "Liên 1 — Người gửi",
        "Liên 2 — Vận chuyển",
        "Liên 3 — Người nhận",
    ]


def test_html_renders_three_a5_copies_from_one_context():
    html = render_bill_html(_bill_fixture())

    assert html.count('class="bill-copy"') == 3
    assert html.count("Nguyễn Văn Gửi") == 3
    assert html.count("NL00001") >= 3
    assert "Phụ phí xăng dầu" in html
    assert "QRCode" not in html


def test_print_context_does_not_truncate_more_than_five_content_lines():
    bill = _bill_fixture()
    bill.content_lines = bill.content_lines * 6

    context = _prepare_context(bill)

    assert len(context["content_lines"]) == 6
    assert context["compact_content"] is True
