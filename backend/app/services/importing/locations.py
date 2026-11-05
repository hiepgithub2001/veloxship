"""Province resolution: canonical ``provinces`` rows + the 2025 merger aliases.

The database holds the 34 post-merger provinces. Customer files still carry the
old names (Hải Dương, Hà Nam, …) plus a few values that were never provinces
(``Hạ Long`` is a city inside Quảng Ninh, ``Chi Nhánh HN`` is an internal
office). This module maps them and reports what was converted.

Pure functions only — the caller passes the province index built from the DB so
this file stays unit-testable without a database.
"""

from __future__ import annotations

import difflib
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from app.services.importing.normalize import (
    clean_text,
    province_key,
    strip_province_prefix,
)

#: Fallback copy of the `provinces` table, used by tests and by the seed helper.
#: The application always prefers the rows read from the database.
PROVINCES: tuple[tuple[str, str], ...] = (
    ("1", "Thành phố Hà Nội"),
    ("4", "Tỉnh Cao Bằng"),
    ("8", "Tỉnh Tuyên Quang"),
    ("11", "Tỉnh Điện Biên"),
    ("12", "Tỉnh Lai Châu"),
    ("14", "Tỉnh Sơn La"),
    ("15", "Tỉnh Lào Cai"),
    ("19", "Tỉnh Thái Nguyên"),
    ("20", "Tỉnh Lạng Sơn"),
    ("22", "Thành phố Quảng Ninh"),
    ("24", "Thành phố Bắc Ninh"),
    ("25", "Tỉnh Phú Thọ"),
    ("31", "Thành phố Hải Phòng"),
    ("33", "Tỉnh Hưng Yên"),
    ("37", "Tỉnh Ninh Bình"),
    ("38", "Tỉnh Thanh Hóa"),
    ("40", "Tỉnh Nghệ An"),
    ("42", "Tỉnh Hà Tĩnh"),
    ("44", "Tỉnh Quảng Trị"),
    ("46", "Thành phố Huế"),
    ("48", "Thành phố Đà Nẵng"),
    ("51", "Tỉnh Quảng Ngãi"),
    ("52", "Tỉnh Gia Lai"),
    ("56", "Tỉnh Khánh Hòa"),
    ("66", "Tỉnh Đắk Lắk"),
    ("68", "Tỉnh Lâm Đồng"),
    ("75", "Thành phố Đồng Nai"),
    ("79", "Thành phố Hồ Chí Minh"),
    ("80", "Tỉnh Tây Ninh"),
    ("82", "Tỉnh Đồng Tháp"),
    ("86", "Tỉnh Vĩnh Long"),
    ("91", "Tỉnh An Giang"),
    ("92", "Thành phố Cần Thơ"),
    ("96", "Tỉnh Cà Mau"),
)

#: Normalised old/alternative name -> canonical province name (as in PROVINCES).
ALIASES: dict[str, str] = {
    # 2025 mergers
    "hai duong": "Hải Phòng",
    "vinh phuc": "Phú Thọ",
    "hoa binh": "Phú Thọ",
    "bac giang": "Bắc Ninh",
    "thai binh": "Hưng Yên",
    "nam dinh": "Ninh Bình",
    "ha nam": "Ninh Bình",
    "yen bai": "Lào Cai",
    "bac kan": "Thái Nguyên",
    "ha giang": "Tuyên Quang",
    "quang binh": "Quảng Trị",
    "kon tum": "Quảng Ngãi",
    "binh dinh": "Gia Lai",
    "phu yen": "Gia Lai",
    "ninh thuan": "Khánh Hòa",
    "dak nong": "Lâm Đồng",
    "binh thuan": "Lâm Đồng",
    "binh phuoc": "Đồng Nai",
    "binh duong": "Hồ Chí Minh",
    "ba ria - vung tau": "Hồ Chí Minh",
    "ba ria vung tau": "Hồ Chí Minh",
    "long an": "Tây Ninh",
    "tien giang": "Đồng Tháp",
    "ben tre": "Vĩnh Long",
    "tra vinh": "Vĩnh Long",
    "kien giang": "An Giang",
    "soc trang": "Cần Thơ",
    "hau giang": "Cần Thơ",
    "bac lieu": "Cà Mau",
    "thua thien hue": "Huế",
    "quang nam": "Đà Nẵng",
    # Not provinces at all
    "ha long": "Quảng Ninh",
    "chi nhanh hn": "Hà Nội",
    # Common shorthand
    "hcm": "Hồ Chí Minh",
    "tphcm": "Hồ Chí Minh",
    "tp hcm": "Hồ Chí Minh",
    "sai gon": "Hồ Chí Minh",
    "hn": "Hà Nội",
}

#: Extra explanation attached when a value was converted through ALIASES.
SPECIAL_NOTES: dict[str, str] = {
    "ha long": "Hạ Long là thành phố thuộc tỉnh Quảng Ninh, không phải tỉnh",
    "chi nhanh hn": "Bưu cục/văn phòng nội bộ, không phải địa chỉ giao",
}

_PREFIX_RE = re.compile(r"^(thanh pho|tinh|tp\.?|tp)\s+")


@dataclass(frozen=True)
class ProvinceResolution:
    """Outcome of resolving one raw destination value."""

    raw: str
    code: str | None = None
    name: str | None = None
    warnings: tuple[str, ...] = field(default=())
    suggestions: tuple[str, ...] = field(default=())

    @property
    def resolved(self) -> bool:
        return self.code is not None and self.name is not None


def build_province_index(
    rows: Iterable[tuple[str, str]] = PROVINCES,
) -> dict[str, tuple[str, str]]:
    """Build ``{matching key: (code, display name)}`` from province rows."""
    index: dict[str, tuple[str, str]] = {}
    for code, name in rows:
        index[province_key(name)] = (code, strip_province_prefix(name))
    return index


def resolve_province(
    value: object,
    index: Mapping[str, tuple[str, str]] | None = None,
) -> ProvinceResolution:
    """Resolve a free-text destination into a canonical province."""
    provinces = index if index is not None else build_province_index()
    raw = clean_text(value)
    if not raw:
        return ProvinceResolution(raw="")

    key = province_key(raw)
    hit = provinces.get(key)
    warnings: list[str] = []

    if hit is None:
        alias = ALIASES.get(key)
        if alias is not None:
            hit = provinces.get(province_key(alias))
            if hit is not None:
                warnings.append(f"'{raw}' → quy đổi '{hit[1]}'")
                note = SPECIAL_NOTES.get(key)
                if note:
                    warnings.append(note)
            else:  # pragma: no cover - aliases point at real provinces
                return ProvinceResolution(raw=raw, warnings=tuple(warnings))

    if hit is None:
        matches = difflib.get_close_matches(key, list(provinces), n=3, cutoff=0.55)
        return ProvinceResolution(
            raw=raw,
            suggestions=tuple(provinces[match][1] for match in matches),
        )

    return ProvinceResolution(
        raw=raw, code=hit[0], name=hit[1], warnings=tuple(warnings)
    )
