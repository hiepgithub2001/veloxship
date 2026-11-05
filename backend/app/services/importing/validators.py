"""Per-row rule engine: raw spreadsheet row -> validated, normalised payload.

Every rule here is pure and DB-free; the caller injects the province index, the
set of tracking numbers that already exist, and the import options.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from app.services.importing.contacts import parse_contact, parse_sender
from app.services.importing.locations import (
    ProvinceResolution,
    build_province_index,
    resolve_province,
)
from app.services.importing.normalize import (
    clean_address,
    clean_text,
    normalize_phone,
    to_decimal,
    to_int,
)
from app.services.importing.readers import RawRow
from app.services.importing.template import FIELD_LABELS, ImportOptions

TRACKING_RE = re.compile(r"^[A-Za-z0-9._\-]+$")
MAX_TRACKING_LENGTH = 50

STATUS_OK = "ok"
STATUS_WARNING = "warning"
STATUS_ERROR = "error"

ERROR_REQUIRED = "IMPORT_ROW_REQUIRED_EMPTY"
ERROR_TRACKING = "IMPORT_TRACKING_INVALID"
ERROR_DUPLICATE_TRACKING = "IMPORT_DUPLICATE_TRACKING"
ERROR_PROVINCE = "IMPORT_PROVINCE_NOT_FOUND"
ERROR_PHONE = "IMPORT_PHONE_INVALID"
ERROR_NUMBER = "IMPORT_NUMBER_INVALID"
ERROR_WEIGHT = "IMPORT_WEIGHT_INVALID"
ERROR_PACKAGES = "IMPORT_QUANTITY_INVALID"


@dataclass(frozen=True)
class ValidationContext:
    """Everything a row needs to know about the outside world."""

    provinces: Mapping[str, tuple[str, str]] = field(
        default_factory=build_province_index
    )
    existing_tracking: frozenset[str] = frozenset()
    options: ImportOptions = field(default_factory=ImportOptions)


@dataclass
class RowValidation:
    """Validation outcome for a single spreadsheet row."""

    row_number: int
    raw: dict[str, Any]
    normalized: dict[str, Any] = field(default_factory=dict)
    status: str = STATUS_OK
    error_code: str | None = None
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)

    @property
    def is_usable(self) -> bool:
        """True when the row may be written (errors are never written)."""
        return self.status != STATUS_ERROR

    @property
    def is_skipped_on_commit(self) -> bool:
        return self.error_code == ERROR_DUPLICATE_TRACKING

    def fail(self, code: str, message: str) -> RowValidation:
        self.status = STATUS_ERROR
        self.error_code = code
        self.error_message = message
        return self

    def warn(self, message: str, code: str | None = None) -> None:
        if message not in self.warnings:
            self.warnings.append(message)
        if self.status == STATUS_OK:
            self.status = STATUS_WARNING
        if code is not None and self.error_code is None:
            self.error_code = code


def _is_blank_cell(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and not value.strip()


def _tracking_value(cells: Mapping[str, Any]) -> str:
    """Read the full tracking number, falling back to prefix + serial."""
    text = clean_text(cells.get("tracking"))
    if text:
        return text
    prefix = clean_text(cells.get("tracking_prefix"))
    serial = clean_text(cells.get("tracking_serial"))
    return f"{prefix}{serial}".strip()


def _title_case(name: str) -> str:
    parts = []
    for word in re.split(r"(\s+)", name):
        if not word.strip():
            parts.append(word)
        else:
            parts.append(word[0].upper() + word[1:].lower())
    return "".join(parts)


def _province_error(resolution: ProvinceResolution) -> str:
    message = f'Không khớp tỉnh/thành nào: "{resolution.raw}".'
    if resolution.suggestions:
        message += f" Có phải ý bạn là: {', '.join(resolution.suggestions)}?"
    return message


def validate_row(
    row: RawRow, context: ValidationContext | None = None
) -> RowValidation:
    """Run every rule for one row and return the normalised payload."""
    ctx = context or ValidationContext()
    options = ctx.options
    cells = row.cells
    result = RowValidation(row_number=row.row_number, raw=dict(cells))
    normalized: dict[str, Any] = {}

    # --- Mã đơn -> tracking number -----------------------------------------
    tracking = _tracking_value(cells)
    if not tracking:
        return result.fail(
            ERROR_REQUIRED, f"Cột bắt buộc đang trống: {FIELD_LABELS['tracking']}."
        )
    if len(tracking) > MAX_TRACKING_LENGTH or not TRACKING_RE.match(tracking):
        return result.fail(
            ERROR_TRACKING,
            f'Mã đơn không hợp lệ: "{tracking}" (chỉ cho phép chữ, số, dấu chấm, '
            f"gạch dưới, gạch ngang; tối đa {MAX_TRACKING_LENGTH} ký tự).",
        )
    normalized["tracking_number"] = tracking

    # --- Địa điểm -> province ------------------------------------------------
    destination_raw = clean_text(cells.get("destination"))
    if not destination_raw:
        return result.fail(
            ERROR_REQUIRED, f"Cột bắt buộc đang trống: {FIELD_LABELS['destination']}."
        )
    resolution = resolve_province(destination_raw, ctx.provinces)
    if not resolution.resolved:
        return result.fail(ERROR_PROVINCE, _province_error(resolution))
    normalized["destination_raw"] = resolution.raw
    normalized["province_code"] = resolution.code
    normalized["province_name"] = resolution.name
    for warning in resolution.warnings:
        result.warn(warning)

    # --- Tên đại lý nhận -----------------------------------------------------
    receiver_name = clean_text(cells.get("receiver_name"))
    if not receiver_name:
        return result.fail(
            ERROR_REQUIRED, f"Cột bắt buộc đang trống: {FIELD_LABELS['receiver_name']}."
        )
    if options.normalize_names and receiver_name.isupper():
        receiver_name = _title_case(receiver_name)
    normalized["receiver_name"] = receiver_name
    normalized["address_detail"] = clean_address(cells.get("address"))

    # --- Liên hệ -------------------------------------------------------------
    # Pass the RAW cell value: `clean_text` would collapse the newlines that
    # separate two contacts sharing one cell.
    contact_cell = cells.get("contact")
    if contact_cell is None or (
        isinstance(contact_cell, str) and not contact_cell.strip()
    ):
        return result.fail(
            ERROR_REQUIRED, f"Cột bắt buộc đang trống: {FIELD_LABELS['contact']}."
        )
    contact = parse_contact(contact_cell)
    if not contact.primary_phone:
        return result.fail(
            ERROR_PHONE, f'Không đọc được số điện thoại từ: "{contact.raw}".'
        )
    normalized["contact_name"] = contact.primary_name
    normalized["contact_phone"] = contact.primary_phone
    normalized["contact_raw"] = contact.raw
    normalized["extra_contacts"] = list(contact.extras)
    if contact.extras:
        result.warn(
            f"Có {len(contact.extras)} liên hệ khác → sẽ tạo bình luận: "
            f"{'; '.join(contact.extras)}"
        )

    # --- Người gửi (tuỳ chọn) ------------------------------------------------
    # Thứ tự ưu tiên: cột trong file -> tuỳ chọn khi import -> mặc định công ty
    # (mặc định do `import_service` áp dụng khi payload không có người gửi).
    sender_name = ""
    sender_phone = ""

    parsed_sender = None
    sender_cell = cells.get("sender")
    if not _is_blank_cell(sender_cell):
        parsed_sender = parse_sender(sender_cell)
        sender_name = parsed_sender.primary_name
        sender_phone = parsed_sender.primary_phone

    sender_phone_cell = cells.get("sender_phone")
    if not _is_blank_cell(sender_phone_cell):
        explicit_phone = normalize_phone(sender_phone_cell)
        if explicit_phone:
            sender_phone = explicit_phone
        else:
            result.warn(
                f'SĐT người gửi không hợp lệ: "{clean_text(sender_phone_cell)}" — bỏ qua.'
            )

    # Only complain once both the combined cell and the dedicated phone column
    # have been considered — "Mr Hải" in one column + the phone in the next is
    # a perfectly normal file.
    if parsed_sender is not None and not sender_phone:
        result.warn(
            f'Không đọc được SĐT người gửi từ "{parsed_sender.raw}" — dùng mặc định.'
        )

    if not sender_name and options.sender_name:
        sender_name = clean_text(options.sender_name)
    if not sender_phone and options.sender_phone:
        sender_phone = normalize_phone(options.sender_phone) or ""
        if not sender_phone:
            result.warn("SĐT người gửi trong tuỳ chọn không hợp lệ — dùng mặc định.")
    if sender_name or sender_phone:
        normalized["sender_name"] = sender_name
        normalized["sender_phone"] = sender_phone

    # --- Số kiện -------------------------------------------------------------
    packages_raw = cells.get("packages")
    packages = to_int(packages_raw)
    if packages is None:
        if clean_text(packages_raw):
            return result.fail(
                ERROR_NUMBER, f'Giá trị số không hợp lệ: "{clean_text(packages_raw)}".'
            )
        packages = options.default_packages
        result.warn(
            f"Số kiện trống → dùng mặc định {options.default_packages}.",
        )
    if packages < 1:
        return result.fail(ERROR_PACKAGES, "Số kiện phải là số nguyên lớn hơn 0.")
    normalized["packages"] = packages

    # --- Trọng lượng ---------------------------------------------------------
    weight = to_decimal(cells.get("weight"))
    if weight is None:
        return result.fail(
            ERROR_WEIGHT,
            f'Trọng lượng không hợp lệ: "{clean_text(cells.get("weight"))}".',
        )
    if weight <= 0:
        return result.fail(ERROR_WEIGHT, "Trọng lượng phải lớn hơn 0.")
    normalized["weight_kg"] = str(weight)

    # --- Số lượng Catalogue (optional, "thông tin thêm") ---------------------
    catalogue_raw = cells.get("catalogue_qty")
    catalogue_quantity = to_int(catalogue_raw)
    if catalogue_quantity is None and clean_text(catalogue_raw):
        result.warn(
            f'Số lượng Catalogue không hợp lệ: "{clean_text(catalogue_raw)}" — bỏ trống.'
        )
        catalogue_quantity = None
    if catalogue_quantity is not None and catalogue_quantity < 0:
        result.warn("Số lượng Catalogue âm — bỏ trống.")
        catalogue_quantity = None
    if catalogue_quantity is not None:
        normalized["catalogue_quantity"] = catalogue_quantity

    # --- Chống trùng mã vận đơn ---------------------------------------------
    if tracking in ctx.existing_tracking:
        result.warn(
            f'Mã vận đơn "{tracking}" đã tồn tại — dòng này sẽ bị bỏ qua.',
            code=ERROR_DUPLICATE_TRACKING,
        )

    result.normalized = normalized
    return result


def duplicate_tracking_warning(tracking: str) -> str:
    """Message used when the same tracking number appears twice in one file."""
    return f'Mã vận đơn "{tracking}" bị lặp trong cùng file — dòng này sẽ bị bỏ qua.'
