"""Unit tests for province resolution and the 2025 merger aliases."""

import pytest

from app.services.importing.locations import (
    ALIASES,
    PROVINCES,
    build_province_index,
    resolve_province,
)
from app.services.importing.normalize import strip_province_prefix

INDEX = build_province_index()


@pytest.mark.parametrize(("code", "name"), PROVINCES)
def test_every_seeded_province_resolves_to_itself(code, name):
    resolution = resolve_province(name, INDEX)
    assert resolution.resolved
    assert resolution.code == code
    assert resolution.warnings == ()


@pytest.mark.parametrize(
    ("raw", "expected_name"),
    [
        ("Hải Dương", "Hải Phòng"),
        ("Vĩnh Phúc", "Phú Thọ"),
        ("Hòa Bình", "Phú Thọ"),
        ("Bắc Giang", "Bắc Ninh"),
        ("Thái Bình", "Hưng Yên"),
        ("Nam Định", "Ninh Bình"),
        ("Hà Nam", "Ninh Bình"),
        ("Yên Bái", "Lào Cai"),
        ("Bắc Kạn", "Thái Nguyên"),
        ("Hà Giang", "Tuyên Quang"),
        ("Quảng Bình", "Quảng Trị"),
        ("Kon Tum", "Quảng Ngãi"),
        ("Bình Định", "Gia Lai"),
        ("Ninh Thuận", "Khánh Hòa"),
        ("Bình Dương", "Hồ Chí Minh"),
        ("Long An", "Tây Ninh"),
        ("Trà Vinh", "Vĩnh Long"),
        ("Kiên Giang", "An Giang"),
        ("Sóc Trăng", "Cần Thơ"),
        ("Bạc Liêu", "Cà Mau"),
        ("Thừa Thiên Huế", "Huế"),
        ("Quảng Nam", "Đà Nẵng"),
    ],
)
def test_merged_provinces_map_to_the_current_name(raw, expected_name):
    resolution = resolve_province(raw, INDEX)
    assert resolution.resolved
    assert resolution.name == expected_name
    assert resolution.warnings, "conversion must be reported so the user sees it"


def test_city_inside_a_province_is_flagged_explicitly():
    resolution = resolve_province("Hạ Long", INDEX)
    assert (resolution.code, resolution.name) == ("22", "Quảng Ninh")
    assert any("thành phố thuộc tỉnh" in warning for warning in resolution.warnings)


def test_internal_office_is_flagged_explicitly():
    resolution = resolve_province("Chi Nhánh HN", INDEX)
    assert (resolution.code, resolution.name) == ("1", "Hà Nội")
    assert any("nội bộ" in warning for warning in resolution.warnings)


@pytest.mark.parametrize(
    "raw",
    [
        "Thành phố Hà Nội",
        "Tỉnh Ninh Bình",
        "TP. Hải Phòng",
        "tp hồ chí minh",
        "  Hà   Nội  ",
        "HÀ NỘI",
        "ha noi",
    ],
)
def test_prefixes_accents_and_case_are_ignored(raw):
    resolution = resolve_province(raw, INDEX)
    assert resolution.resolved
    assert resolution.name in {"Hà Nội", "Ninh Bình", "Hải Phòng", "Hồ Chí Minh"}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("HCM", "Hồ Chí Minh"),
        ("TPHCM", "Hồ Chí Minh"),
        ("Sài Gòn", "Hồ Chí Minh"),
    ],
)
def test_common_shorthand_maps_to_ho_chi_minh(raw, expected):
    resolution = resolve_province(raw, INDEX)
    assert resolution.name == expected


def test_unknown_value_returns_suggestions_instead_of_guessing():
    resolution = resolve_province("Hà Nội 2", INDEX)
    assert resolution.resolved is False
    assert "Hà Nội" in resolution.suggestions


def test_empty_value_is_not_resolved():
    resolution = resolve_province("   ", INDEX)
    assert resolution.resolved is False
    assert resolution.raw == ""


def test_alias_targets_always_exist_in_the_seeded_list():
    names = {strip_province_prefix(name) for _, name in PROVINCES}
    assert set(ALIASES.values()) <= names
