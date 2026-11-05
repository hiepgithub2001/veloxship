"""Contact-cell parser: one primary contact + any number of extras.

Real files pack one or two people into a single ``Liên hệ`` cell, written in a
dozen different shapes. The rules below were validated against all 70 rows of
the reference file ``5.11 Mr Hải Logex.xlsx``:

    'Chị Hương: 0949988999'                       -> Hương / 0949988999
    'Chị Loan 0983280816/ Ngọc 0973319660'        -> Loan  / 0983280816  + Ngọc
    '(024) 3853 2294\\nChị Hoa: 0868327760'        -> Hoa   / 0868327760  + landline
    'SR 1: Ms. Thoa 0972 173 867\\nSR 2: ...'      -> Thoa  / 0972173867  + Nghĩa
    'Mr. Thành \\n0911 166 177'                    -> Thành / 0911166177
    '0938888838 (Mrs. Thơ)'                       -> Thơ   / 0938888838
    'ms.Anh 0365446686'                           -> Anh   / 0365446686
    '02253 591 335 - 0929 853 969'                -> (none)/ 02253591335 + 0929853969
    'Đầo Mai - 033 863 2357'                      -> Đầo Mai/0338632357

Pure functions only — no database, no I/O.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.services.importing.normalize import normalize_phone

# Honorifics stripped from the start of a name, longest first so "chi" cannot
# eat "chị". "anh" is also a real given name — see _clean_name.
_HONORIFICS = (
    "chị",
    "chi",
    "anh",
    "annh",
    "em",
    "cô",
    "co",
    "bác",
    "bac",
    "ông",
    "ong",
    "chú",
    "chu",
    "thầy",
    "ms",
    "mrs",
    "mr",
    "miss",
    "c",
    "a",
    "đ/c",
    "đc",
    "dc",
)
_HONORIFIC_RE = re.compile(
    r"^(?:" + "|".join(re.escape(token) for token in _HONORIFICS) + r")"
    r"\s*[.,:\-]?\s*",
    re.IGNORECASE,
)
_NOISE_RE = re.compile(
    r"\b(hot\s*line|hotline|đường\s*dây\s*nóng|sđt|đt|điện\s*thoại|tel|phone)\b"
    r"\s*[:.\-]?\s*",
    re.IGNORECASE,
)
_BRANCH_RE = re.compile(
    r"^\s*(?:sr|showroom|cửa\s*hàng|cn|chi\s*nhánh)\s*\d*\s*[:.\-]\s*",
    re.IGNORECASE,
)
_EDGE_PUNCT_RE = re.compile(r"^[\s\-–—:.,;/|()\[\]'\"]+|[\s\-–—:.,;/|()\[\]'\"]+$")
_QUOTES_RE = re.compile(r"['\u2018\u2019\u201c\u201d]")
_PHONE_RE = re.compile(r"(?:\+?84|0)\d[\d\s.\-()]{4,16}\d")
_SEPARATOR_RE = re.compile(r"\s*(?:\n|/|–|—|\s-\s)\s*")
_HAS_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)
# Collapse runs of blanks but KEEP newlines: they are a contact separator.
_INLINE_SPACE_RE = re.compile(r"[^\S\n]+")


@dataclass(frozen=True)
class ParsedContact:
    """Result of parsing one raw contact cell."""

    raw: str
    primary_name: str
    primary_phone: str
    extras: tuple[str, ...] = field(default=())

    @property
    def has_primary(self) -> bool:
        return bool(self.primary_name or self.primary_phone)

    @property
    def all_entries(self) -> tuple[str, ...]:
        """Primary + extras, formatted for a comment body."""
        primary = " - ".join(
            part for part in (self.primary_name, self.primary_phone) if part
        )
        return tuple(entry for entry in (primary, *self.extras) if entry)


def _raw_text(value: Any) -> str:
    """Cell text that keeps line breaks (they separate two contacts)."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        text = str(int(value)) if value.is_integer() else repr(value)
    else:
        text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _INLINE_SPACE_RE.sub(" ", text).strip()


def _split_fragments(raw: str) -> list[str]:
    text = _QUOTES_RE.sub("", raw)
    return [part.strip() for part in _SEPARATOR_RE.split(text) if part and part.strip()]


def _clean_name(fragment: str) -> str:
    text = _BRANCH_RE.sub("", fragment)
    text = _NOISE_RE.sub(" ", text)
    text = _QUOTES_RE.sub("", text)
    text = _INLINE_SPACE_RE.sub(" ", text)
    text = _EDGE_PUNCT_RE.sub("", text.strip())
    for _ in range(6):
        match = _HONORIFIC_RE.match(text)
        if not match:
            break
        remainder = _EDGE_PUNCT_RE.sub("", text[match.end() :].strip())
        # Never strip the only remaining word: "Anh" alone is the person's name,
        # and a trailing phone group is not a name either.
        if not remainder or not _HAS_LETTER_RE.search(remainder):
            break
        text = remainder
    return _INLINE_SPACE_RE.sub(" ", text).strip()


def _extract_phones(fragment: str) -> list[tuple[str, str]]:
    """Return ``(raw_text, normalised)`` for every phone in a fragment."""
    phones: list[tuple[str, str]] = []
    for match in _PHONE_RE.finditer(fragment):
        raw_phone = match.group(0).strip()
        phone = normalize_phone(raw_phone)
        if phone and phone not in {item[1] for item in phones}:
            phones.append((raw_phone, phone))
    return phones


def parse_contact(value: Any) -> ParsedContact:
    """Split one ``Liên hệ`` cell into a primary contact plus extras."""
    raw = _raw_text(value)
    if not raw:
        return ParsedContact(raw="", primary_name="", primary_phone="")

    fragments: list[dict[str, str]] = []
    for fragment in _split_fragments(raw):
        phones = _extract_phones(fragment)
        name = _clean_name(fragment)
        for raw_phone, _normalised in phones:
            name = name.replace(raw_phone, " ")
        name = _clean_name(name)
        if phones:
            for _raw_phone, phone in phones:
                fragments.append({"name": name, "phone": phone})
        elif name:
            fragments.append({"name": name, "phone": ""})

    # Merge an orphan name with the phone fragment that follows it:
    #   "Mr. Thành" / "0911 166 177"  ->  ("Thành", "0911166177")
    merged: list[dict[str, str]] = []
    index = 0
    while index < len(fragments):
        current = dict(fragments[index])
        cursor = index + 1
        while (
            not current["phone"]
            and cursor < len(fragments)
            and fragments[cursor]["phone"]
        ):
            current["phone"] = fragments[cursor]["phone"]
            if not current["name"]:
                current["name"] = fragments[cursor]["name"]
            fragments[cursor] = {"name": fragments[cursor]["name"], "phone": ""}
            cursor += 1
        merged.append(current)
        index += 1
    fragments = [item for item in merged if item["name"] or item["phone"]]

    if not fragments:
        return ParsedContact(raw=raw, primary_name="", primary_phone="")

    primary = next((item for item in fragments if item["name"] and item["phone"]), None)
    if primary is None:
        primary = next((item for item in fragments if item["phone"]), None)
    if primary is None:
        primary = fragments[0]

    extras: list[str] = []
    for item in fragments:
        if item is primary:
            continue
        if not (item["name"] or item["phone"]):
            continue
        # A repeated number is not a second contact.
        if item["phone"] and item["phone"] == primary["phone"]:
            continue
        label = " - ".join(part for part in (item["name"], item["phone"]) if part)
        if label and label not in extras:
            extras.append(label)

    return ParsedContact(
        raw=raw,
        primary_name=primary["name"],
        primary_phone=primary["phone"],
        extras=tuple(extras),
    )


def format_extra_contacts(extras: list[str] | tuple[str, ...]) -> str:
    """Render the extras as the plain-text body used inside the comment."""
    return "; ".join(extras)


def parse_sender(value: Any) -> ParsedContact:
    """Parse a sender cell, **keeping honorifics** (unlike :func:`parse_contact`).

    A receiver contact is a person the shipper phones, so "Chị Hương" should be
    stored as "Hương". A sender, on the other hand, is the party printed on the
    bill — "Mr Hải" must stay "Mr Hải", not become "Hải".
    """
    raw = _raw_text(value)
    if not raw:
        return ParsedContact(raw="", primary_name="", primary_phone="")

    phones = _extract_phones(raw)
    name = raw
    phone = ""
    for raw_phone, normalised in phones:
        name = name.replace(raw_phone, " ")
        if not phone:
            phone = normalised
    name = re.sub(r"\s{2,}", " ", name)
    name = _EDGE_PUNCT_RE.sub("", name.strip())
    return ParsedContact(raw=raw, primary_name=name, primary_phone=phone)
