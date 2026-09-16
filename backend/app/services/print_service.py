"""Print service — renders the canonical A5 delivery bill to HTML and PDF."""

import base64
import io
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import barcode
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

_TEMPLATE_DIR = Path(__file__).parent.parent / "static"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)

_DOMESTIC_SERVICES = (
    ("CPN", "CPN"),
    ("PHT", "PHT"),
    ("DUONG_BO", "Đường bộ"),
    ("T48H", "48H"),
    ("NGUYEN_CHUYEN", "Nguyên chuyến"),
    ("KHAC", "Khác"),
)
_INTERNATIONAL_SERVICES = (
    ("INTL_EXPRESS", "Express"),
    ("INTL_ECONOMY", "Economy"),
    ("INTL_OTHER", "Other"),
)
_COPY_LABELS = (
    "Liên 1 — Người gửi",
    "Liên 2 — Vận chuyển",
    "Liên 3 — Người nhận",
)


def _asset_data_uri(filename: str, mime_type: str) -> str:
    encoded = base64.b64encode((_TEMPLATE_DIR / filename).read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _generate_barcode_svg(tracking_number: str) -> str:
    """Generate a compact Code 128 barcode as inline SVG."""
    code128 = barcode.get("code128", tracking_number, writer=barcode.writer.SVGWriter())
    svg_io = io.BytesIO()
    code128.write(
        svg_io,
        options={
            "write_text": False,
            "module_height": 10,
            "quiet_zone": 1.5,
            "font_size": 0,
        },
    )
    return svg_io.getvalue().decode("utf-8")


def _format_vnd(amount: Decimal | int | float | None) -> str:
    """Format a number as whole Vietnamese đồng with dot separators."""
    if amount is None:
        return "0"
    return f"{int(Decimal(str(amount))):,}".replace(",", ".")


def _format_number(value: Decimal | int | float | None, decimals: int = 2) -> str:
    """Format a decimal using Vietnamese separators without a unit suffix."""
    if value is None:
        return ""
    rendered = f"{Decimal(str(value)):,.{decimals}f}"
    return rendered.replace(",", "X").replace(".", ",").replace("X", ".")


def _format_dimension(value: Decimal | int | float | None) -> str:
    if value is None:
        return ""
    number = Decimal(str(value))
    if number == number.to_integral():
        return str(int(number))
    return _format_number(number, 1)


def _party_context(customer, snapshot: dict | None) -> dict[str, str]:
    """Build historical party details from the immutable bill snapshot."""
    data = snapshot or {}
    if not data and customer is not None:
        metadata = customer.customer_metadata or {}
        data = {
            "name": customer.name,
            "phone": customer.phone,
            "address_detail": metadata.get("address_detail"),
            "province_name": metadata.get("province_name"),
            "ward_name": metadata.get("ward_name"),
        }
    return {
        "code": data.get("code")
        or (customer.code if customer is not None else None)
        or "KH-LẺ",
        "name": data.get("name") or "",
        "phone": data.get("phone") or "",
        "address_detail": data.get("address_detail") or "",
        "district_name": data.get("district_name") or "—",
        "province_name": data.get("province_name") or "",
        "ward_name": data.get("ward_name") or "",
    }


def _service_options(
    selected_code: str | None, options: tuple[tuple[str, str], ...]
) -> list[dict]:
    return [
        {"code": code, "label": label, "checked": selected_code == code}
        for code, label in options
    ]


def _local_bill_date(value: datetime | None) -> datetime:
    bill_date = value or datetime.now(UTC)
    if bill_date.tzinfo is None:
        bill_date = bill_date.replace(tzinfo=UTC)
    return bill_date.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))


def _prepare_context(bill) -> dict:
    """Build a renderer-only context from a fully loaded bill model."""
    content_lines = []
    for line in bill.content_lines:
        content_lines.append(
            {
                "description": line.description,
                "quantity": line.quantity,
                "weight": _format_number(line.weight_kg),
                "length": _format_dimension(line.length_cm),
                "width": _format_dimension(line.width_cm),
                "height": _format_dimension(line.height_cm),
                "is_blank": False,
            }
        )
    content_lines.extend(
        {
            "description": "",
            "quantity": "",
            "weight": "",
            "length": "",
            "width": "",
            "height": "",
            "is_blank": True,
        }
        for _ in range(max(0, 5 - len(content_lines)))
    )

    service_code = bill.service_tier_code
    service_scope = getattr(bill.service_tier, "scope", None)
    if service_scope is None and service_code:
        service_scope = (
            "international" if service_code.startswith("INTL_") else "domestic"
        )

    copy_count = max(1, min(int(settings.BILL_PDF_COPY_COUNT), len(_COPY_LABELS)))
    bill_date = _local_bill_date(bill.created_at)

    return {
        "tracking_number": bill.tracking_number,
        "print_css": (_TEMPLATE_DIR / "print.css").read_text(encoding="utf-8"),
        "logo_data_uri": _asset_data_uri("logo.png", "image/png"),
        "sender": _party_context(bill.sender, bill.sender_snapshot),
        "receiver": _party_context(bill.receiver, bill.receiver_snapshot),
        "barcode_svg": _generate_barcode_svg(bill.tracking_number),
        "content_lines": content_lines,
        "compact_content": len(bill.content_lines) > 5,
        "actual_weight": _format_number(bill.actual_weight_kg),
        "chargeable_weight": _format_number(bill.chargeable_weight_kg),
        "cod_amount": _format_vnd(bill.cod_amount),
        "fee_main": _format_vnd(bill.fee_main),
        "fee_fuel_surcharge": "0",
        "fee_insurance": _format_vnd(bill.fee_insurance),
        "fee_other": _format_vnd(bill.fee_other),
        "fee_vat": _format_vnd(bill.fee_vat),
        "fee_total": _format_vnd(bill.fee_total),
        "is_sender_payer": bill.payer == "sender",
        "is_document": bill.cargo_type == "document",
        "is_domestic": service_scope == "domestic",
        "is_international": service_scope == "international",
        "domestic_services": _service_options(service_code, _DOMESTIC_SERVICES),
        "international_services": _service_options(
            service_code, _INTERNATIONAL_SERVICES
        ),
        "date_day": bill_date.strftime("%d"),
        "date_month": bill_date.strftime("%m"),
        "date_year": bill_date.strftime("%Y"),
        "copies": [{"label": label} for label in _COPY_LABELS[:copy_count]],
        "carrier_name": settings.CARRIER_NAME,
        "carrier_hotline": settings.CARRIER_HOTLINE,
        "carrier_email": settings.CARRIER_EMAIL,
    }


def render_bill_html(bill) -> str:
    """Render the bill to standalone HTML."""
    template = _env.get_template("bill_template.html")
    return template.render(**_prepare_context(bill))


def render_bill_pdf(bill) -> bytes:
    """Render the bill to a three-copy A5 PDF via WeasyPrint."""
    html_str = render_bill_html(bill)
    try:
        from weasyprint import HTML

        return HTML(string=html_str, base_url=str(_TEMPLATE_DIR)).write_pdf()
    except ImportError:
        # Local development may omit WeasyPrint's native dependencies.
        return html_str.encode("utf-8")
