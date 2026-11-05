"""Unit tests for the importer's normalisation helpers."""

from decimal import Decimal

import pytest

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


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Shapes taken verbatim from the reference file.
        ("'0976758807", "0976758807"),
        ("(024) 3853 2294", "02438532294"),
        ("091 9889994", "0919889994"),
        ("02283 680 440", "02283680440"),
        ("0936 599 559", "0936599559"),
        ("+84 90 123 4567", "0901234567"),
        ("84 90 123 4567", "0901234567"),
        ("0901234567", "0901234567"),
        # Too short / too long / unusable.
        ("091234", None),
        ("1234567890123", None),
        ("", None),
        (None, None),
        ("abc", None),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # The reference file stores 29 as 28.999999999999996.
        (28.999999999999996, Decimal("29.000")),
        (14.499999999999998, Decimal("14.500")),
        (43.5, Decimal("43.500")),
        ("43,5", Decimal("43.500")),
        ("1.234,5", Decimal("1234.500")),
        (0, Decimal("0.000")),
    ],
)
def test_to_decimal_quantises_float_noise(raw, expected):
    assert to_decimal(raw) == expected


@pytest.mark.parametrize("raw", [None, "", "  ", "abc", True])
def test_to_decimal_rejects_unusable_values(raw):
    assert to_decimal(raw) is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (3.0, 3),
        (3, 3),
        ("3", 3),
        (" 12 ", 12),
        (3.5, None),
        ("3,5", None),
        (None, None),
        ("", None),
        ("abc", None),
        (True, None),
    ],
)
def test_to_int_rejects_fractional_values(raw, expected):
    assert to_int(raw) == expected


def test_clean_text_renders_integral_floats_without_decimals():
    assert clean_text(150.0) == "150"
    assert clean_text(43.5) == "43.5"
    assert clean_text("  Hà   Nội  ") == "Hà Nội"
    assert clean_text(None) == ""


def test_clean_address_keeps_the_written_content():
    raw = "B2 10 Shop house 24H Đường Tố Hữu, Phường Hà Đông, Hà Nội."
    assert clean_address(raw) == raw
    # Only surrounding/duplicated blanks are collapsed.
    assert clean_address("  Số   7,  lô 4A ") == "Số 7, lô 4A"


def test_strip_diacritics_handles_d_stroke():
    assert strip_diacritics("Đường Đầm") == "Duong Dam"


def test_normalize_key_is_accent_and_case_insensitive():
    assert normalize_key("  SỐ   KIỆN ") == "so kien"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Thành phố Hà Nội", "ha noi"),
        ("Tỉnh Ninh Bình", "ninh binh"),
        ("TP. Hồ Chí Minh", "ho chi minh"),
        ("Hải Dương", "hai duong"),
    ],
)
def test_province_key_strips_the_admin_prefix(raw, expected):
    assert province_key(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Thành phố Hà Nội", "Hà Nội"),
        ("Tỉnh Ninh Bình", "Ninh Bình"),
        ("TP. Huế", "Huế"),
        ("Lào Cai", "Lào Cai"),
    ],
)
def test_strip_province_prefix_keeps_the_accents(raw, expected):
    assert strip_province_prefix(raw) == expected
