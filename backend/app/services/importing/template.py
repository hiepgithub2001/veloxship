"""Declarative description of the importable spreadsheet columns.

This module is the **single source of truth**: the reader uses the header
dictionary to find columns, the validator uses the field labels to build error
messages, and the result exporter reuses them. Adding a column means touching
only this file.

Pure data — no I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.importing.normalize import normalize_key


@dataclass(frozen=True)
class FieldSpec:
    """One logical field of the import source."""

    key: str
    label: str
    aliases: tuple[str, ...]
    required: bool = False


#: Fields of the reference file layout (``5.11 Mr Hải Logex.xlsx``).
#: Aliases are accent-insensitive and lowercase; see ``HEADER_LOOKUP``.
BILL_FIELDS: tuple[FieldSpec, ...] = (
    FieldSpec(
        key="tracking",
        label="Mã đơn",
        aliases=("ma don", "ma van don", "ma phieu", "so van don", "code"),
        required=True,
    ),
    FieldSpec(
        key="destination",
        label="Địa điểm giao",
        aliases=(
            "dia diem giao",
            "dia diem",
            "tinh thanh pho giao",
            "tinh giao",
            "tinh",
        ),
        required=True,
    ),
    FieldSpec(
        key="receiver_name",
        label="Tên đại lý nhận",
        aliases=(
            "ten dai ly nhan",
            "ten dai ly",
            "ten khach hang nhan",
            "ten khach nhan",
            "khach hang",
            "ten khach hang",
        ),
        required=True,
    ),
    FieldSpec(
        key="address",
        label="Địa chỉ giao chi tiết",
        aliases=("dia chi giao chi tiet", "dia chi giao", "dia chi"),
    ),
    FieldSpec(
        key="contact",
        label="Liên hệ",
        aliases=("lien he", "thong tin lien he", "nguoi lien he", "dien thoai", "sdt"),
        required=True,
    ),
    FieldSpec(
        key="catalogue_qty",
        label="Số lượng Catalogue",
        aliases=("so luong catalogue", "so luong catalog", "so luong", "catalogue"),
    ),
    FieldSpec(
        key="packages",
        label="Số kiện",
        aliases=("so kien", "kien"),
        required=True,
    ),
    FieldSpec(
        key="weight",
        label="Trọng lượng (kg)",
        aliases=("trong luong (kg)", "trong luong", "khoi luong", "kg"),
        required=True,
    ),
    FieldSpec(
        key="tracking_prefix",
        label="Tiền tố mã đơn",
        aliases=("tien to", "prefix"),
    ),
    # Optional sender columns. When missing, the import falls back to the
    # per-import `sender_name` / `sender_phone` option and finally to the
    # company configured in settings (CARRIER_NAME / CARRIER_HOTLINE).
    FieldSpec(
        key="sender",
        label="Người gửi",
        aliases=(
            "nguoi gui",
            "ten nguoi gui",
            "thong tin nguoi gui",
            "lien he nguoi gui",
            "sender",
        ),
    ),
    FieldSpec(
        key="sender_phone",
        label="SĐT người gửi",
        aliases=(
            "sdt nguoi gui",
            "so dien thoai nguoi gui",
            "dien thoai nguoi gui",
            "phone nguoi gui",
        ),
    ),
)

#: Alias -> field key lookup used by the reader. ``tracking`` aliases are kept
#: separate because a file may repeat the "Mã đơn" header on two columns.
HEADER_LOOKUP: dict[str, str] = {}
for _field in BILL_FIELDS:
    for _alias in _field.aliases:
        HEADER_LOOKUP.setdefault(normalize_key(_alias), _field.key)

TRACKING_ALIASES: frozenset[str] = frozenset(
    normalize_key(alias)
    for _field in BILL_FIELDS
    if _field.key == "tracking"
    for alias in _field.aliases
)
PREFIX_ALIASES: frozenset[str] = frozenset(
    normalize_key(alias)
    for _field in BILL_FIELDS
    if _field.key == "tracking_prefix"
    for alias in _field.aliases
)

FIELD_LABELS: dict[str, str] = {_field.key: _field.label for _field in BILL_FIELDS}

REQUIRED_FIELDS: tuple[str, ...] = tuple(
    _field.key for _field in BILL_FIELDS if _field.required
)


@dataclass(frozen=True)
class ImportOptions:
    """Behaviour switches that the caller may override per import."""

    catalogue_description: str = "Catalogue"
    default_packages: int = 1
    normalize_names: bool = False
    max_rows: int = 5000
    #: Optional sender applied to rows whose file has no sender column.
    sender_name: str | None = None
    sender_phone: str | None = None


def parse_options(raw: dict[str, Any] | None) -> ImportOptions:
    """Build options from an untrusted JSON dict, ignoring unknown keys."""
    if not raw:
        return ImportOptions()
    data = raw if isinstance(raw, dict) else {}

    description = data.get("catalogue_description")
    if not isinstance(description, str) or not description.strip():
        description = ImportOptions.catalogue_description

    packages = data.get("default_packages")
    try:
        default_packages = int(packages)
    except (TypeError, ValueError):
        default_packages = ImportOptions.default_packages
    if default_packages < 1:
        default_packages = ImportOptions.default_packages

    def _optional_text(key: str) -> str | None:
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            return None
        return value.strip()

    return ImportOptions(
        catalogue_description=description.strip(),
        default_packages=default_packages,
        normalize_names=bool(data.get("normalize_names", False)),
        max_rows=ImportOptions.max_rows,
        sender_name=_optional_text("sender_name"),
        sender_phone=_optional_text("sender_phone"),
    )
