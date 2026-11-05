"""Pure helper package for the Excel importer.

Mirrors ``app/services/storage/``: this package holds **pure functions and
constants only** — no database session, no file upload, no side effects. The
orchestration lives in ``app/services/import_service.py``.

Being pure is what lets the whole parsing/normalisation layer be unit-tested
without a database.
"""

from app.services.importing.contacts import (
    ParsedContact,
    format_extra_contacts,
    parse_contact,
)
from app.services.importing.locations import (
    ALIASES,
    PROVINCES,
    ProvinceResolution,
    build_province_index,
    resolve_province,
)
from app.services.importing.normalize import (
    clean_address,
    clean_text,
    normalize_key,
    normalize_phone,
    province_key,
    strip_diacritics,
    strip_province_prefix,
    to_decimal,
    to_int,
)
from app.services.importing.readers import (
    DetectedLayout,
    LayoutDetection,
    RawRow,
    RowLimitExceeded,
    detect_layout,
    iter_raw_rows,
    load_workbook_from_bytes,
)
from app.services.importing.template import (
    BILL_FIELDS,
    FIELD_LABELS,
    REQUIRED_FIELDS,
    FieldSpec,
    ImportOptions,
    parse_options,
)
from app.services.importing.validators import (
    RowValidation,
    ValidationContext,
    validate_row,
)

__all__ = [
    "ALIASES",
    "BILL_FIELDS",
    "DetectedLayout",
    "FIELD_LABELS",
    "FieldSpec",
    "ImportOptions",
    "LayoutDetection",
    "PROVINCES",
    "ParsedContact",
    "ProvinceResolution",
    "REQUIRED_FIELDS",
    "RawRow",
    "RowLimitExceeded",
    "RowValidation",
    "ValidationContext",
    "build_province_index",
    "clean_address",
    "clean_text",
    "detect_layout",
    "format_extra_contacts",
    "iter_raw_rows",
    "load_workbook_from_bytes",
    "normalize_key",
    "normalize_phone",
    "parse_contact",
    "parse_options",
    "parse_sender",
    "province_key",
    "resolve_province",
    "strip_diacritics",
    "strip_province_prefix",
    "to_decimal",
    "to_int",
    "validate_row",
]
