"""Normalisation helpers for the Excel importer.

Pure functions only — no database, no I/O, no framework imports. Everything in
this module is unit-testable without a running application.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

_WHITESPACE_RE = re.compile(r"\s+")
_NON_DIGIT_RE = re.compile(r"\D")
_VN_PROVINCE_PREFIX_RE = re.compile(r"^(thanh pho|tinh|tp\.?|tp)\s+")
_QUOTES_RE = re.compile(r"['\u2018\u2019\u201c\u201d]")


def strip_diacritics(text: str) -> str:
    """Remove Vietnamese accents, including the non-decomposable ``đ``."""
    decomposed = unicodedata.normalize("NFD", text)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    return without_marks.replace("đ", "d").replace("Đ", "D")


def normalize_key(value: Any) -> str:
    """Return an accent-insensitive, lowercase, single-spaced matching key."""
    if value is None:
        return ""
    text = strip_diacritics(str(value)).lower()
    return _WHITESPACE_RE.sub(" ", text).strip()


def strip_province_prefix(value: str) -> str:
    """Drop a leading ``Tỉnh`` / ``Thành phố`` / ``TP.`` from a province name."""
    return re.sub(
        r"^(thành phố|tỉnh|tp\.?|tp)\s+", "", value.strip(), flags=re.IGNORECASE
    ).strip()


def province_key(value: Any) -> str:
    """Matching key for a province, ignoring accents and the admin prefix."""
    return _VN_PROVINCE_PREFIX_RE.sub("", normalize_key(value)).strip()


def clean_text(value: Any) -> str:
    """Convert a spreadsheet cell to text: no ``5.0``, no duplicated spaces."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        text = str(int(value)) if value.is_integer() else repr(value)
    elif isinstance(value, Decimal):
        text = format(value, "f")
    else:
        text = str(value)
    return _WHITESPACE_RE.sub(" ", text).strip()


def clean_address(value: Any) -> str:
    """Clean a free-text address but never rewrite its content.

    Only the leading/trailing whitespace and runs of blanks are collapsed so the
    stored address still matches what the customer sees in the Excel file.
    """
    return clean_text(value)


def normalize_phone(value: Any) -> str | None:
    """Return a 9–11 digit phone number, or ``None`` when it cannot be read.

    Handles the shapes found in real files: ``'0976758807`` (stray apostrophe),
    ``(024) 3853 2294`` (landline grouping), ``091 9889994`` (split groups) and
    ``+84 90 123 4567``.
    """
    text = _QUOTES_RE.sub("", clean_text(value))
    if not text:
        return None
    text = re.sub(r"^\s*\+\s*84", "0", text)
    digits = _NON_DIGIT_RE.sub("", text)
    if digits.startswith("84") and len(digits) > 10:
        digits = "0" + digits[2:]
    if 9 <= len(digits) <= 11:
        return digits
    return None


def to_decimal(value: Any, *, places: int = 3) -> Decimal | None:
    """Parse a number and quantise it to ``places`` decimals.

    Cells such as ``28.999999999999996`` become ``29.000`` so the stored value
    is exact and reconciles with the customer's own spreadsheet.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if isinstance(value, (int, float, Decimal)):
        raw = Decimal(str(value))
    else:
        text = str(value).strip().replace(" ", "").replace("\u00a0", "")
        if "," in text and "." in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text:
            text = text.replace(",", ".")
        try:
            raw = Decimal(text)
        except InvalidOperation:
            return None
    if not raw.is_finite():
        return None
    quantum = Decimal(1).scaleb(-places)
    return raw.quantize(quantum, rounding=ROUND_HALF_UP)


def to_int(value: Any) -> int | None:
    """Parse a strictly integral number, rejecting ``3.5`` instead of rounding."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if isinstance(value, (int, float, Decimal)):
        raw = Decimal(str(value))
    else:
        text = str(value).strip().replace(" ", "")
        try:
            raw = Decimal(text)
        except InvalidOperation:
            return None
    if not raw.is_finite() or raw != raw.to_integral_value():
        return None
    return int(raw)
