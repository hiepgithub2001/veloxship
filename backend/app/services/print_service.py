"""Print service — renders bill to HTML and PDF."""

import base64
import io

import barcode
import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.core.config import settings

_TEMPLATE_DIR = Path(__file__).parent.parent / "static"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def _generate_barcode_svg(tracking_number: str) -> str:
    """Generate a Code128 barcode as inline SVG."""
    code128 = barcode.get("code128", tracking_number, writer=barcode.writer.SVGWriter())
    svg_io = io.BytesIO()
    code128.write(svg_io, options={"write_text": False, "module_height": 12})
    return svg_io.getvalue().decode("utf-8")


def _generate_qr_base64(tracking_number: str) -> str:
    """Generate a QR code as base64-encoded PNG."""
    url = f"https://{settings.CARRIER_WEBSITE}/tra-cuu/{tracking_number}"
    qr = qrcode.make(url, box_size=4, border=1)
    img_io = io.BytesIO()
    qr.save(img_io, format="PNG")
    return base64.b64encode(img_io.getvalue()).decode("utf-8")


def _format_vnd(amount) -> str:
    """Format a number as VND with dot separator."""
    if amount is None:
        return "0"
    return f"{int(amount):,}".replace(",", ".")


def _format_weight(weight) -> str:
    """Format weight with comma decimal."""
    if weight is None:
        return "0,00"
    return f"{float(weight):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _prepare_context(bill) -> dict:
    """Build the template rendering context from a bill model."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    # Content lines
    content_lines = []
    total_weight = 0
    total_quantity = 0
    for line in bill.content_lines:
        dimensions = ""
        if line.length_cm or line.width_cm or line.height_cm:
            parts = []
            if line.length_cm:
                parts.append(f"{float(line.length_cm):.0f}")
            if line.width_cm:
                parts.append(f"{float(line.width_cm):.0f}")
            if line.height_cm:
                parts.append(f"{float(line.height_cm):.0f}")
            dimensions = " × ".join(parts) + " cm"

        content_lines.append({
            "line_no": line.line_no,
            "description": line.description,
            "quantity": line.quantity,
            "weight": _format_weight(line.weight_kg),
            "dimensions": dimensions,
        })
        total_weight += float(line.weight_kg)
        total_quantity += line.quantity

    return {
        "bill": bill,
        "barcode_svg": _generate_barcode_svg(bill.tracking_number),
        "qr_base64": _generate_qr_base64(bill.tracking_number),
        "content_lines": content_lines,
        "total_weight": _format_weight(total_weight),
        "total_quantity": total_quantity,
        "fee_main": _format_vnd(bill.fee_main),
        "fee_fuel": _format_vnd(bill.fee_fuel_surcharge),
        "fee_other": _format_vnd(bill.fee_other_surcharge),
        "fee_vat": _format_vnd(bill.fee_vat),
        "fee_total": _format_vnd(bill.fee_total),
        "is_sender_payer": bill.payer == "sender",
        "is_document": bill.cargo_type == "document",
        "date_day": now.strftime("%d"),
        "date_month": now.strftime("%m"),
        "date_year": now.strftime("%Y"),
        "carrier_name": settings.CARRIER_NAME,
        "carrier_hotline": settings.CARRIER_HOTLINE,
        "carrier_website": settings.CARRIER_WEBSITE,
        "carrier_email": settings.CARRIER_EMAIL,
    }


def render_bill_html(bill) -> str:
    """Render the bill to HTML."""
    template = _env.get_template("bill_template.html")
    context = _prepare_context(bill)
    return template.render(**context)


def render_bill_pdf(bill) -> bytes:
    """Render the bill to PDF via WeasyPrint."""
    html_str = render_bill_html(bill)
    try:
        from weasyprint import HTML
        return HTML(string=html_str, base_url=str(_TEMPLATE_DIR)).write_pdf()
    except ImportError:
        # WeasyPrint not available (dev without native deps) — return HTML as UTF-8
        return html_str.encode("utf-8")
