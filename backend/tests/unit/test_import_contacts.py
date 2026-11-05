"""Unit tests for the contact-cell parser.

Every string in ``REFERENCE_CASES`` is copied verbatim from the customer's file
``5.11 Mr Hải Logex.xlsx`` — that is the whole point: the rules were derived from
real data, so they are pinned to real data.
"""

import pytest

from app.services.importing.contacts import (
    format_extra_contacts,
    parse_contact,
    parse_sender,
)

REFERENCE_CASES = [
    # (raw cell, primary name, primary phone, extras)
    ("Chị Hương: 0949988999", "Hương", "0949988999", ()),
    ("Em Kiên: 0961357756", "Kiên", "0961357756", ()),
    ("Ms My: 0989222768", "My", "0989222768", ()),
    ("Huyền: 0947186556", "Huyền", "0947186556", ()),
    ("anh Minh 0913317668", "Minh", "0913317668", ()),
    ("Ms. Loan: '0976758807", "Loan", "0976758807", ()),
    ("Ms. Hiền\n0906034666", "Hiền", "0906034666", ()),
    ("Mr. Thành \n0911 166 177", "Thành", "0911166177", ()),
    ("0938888838 (Mrs. Thơ)", "Thơ", "0938888838", ()),
    ("ms.Anh 0365446686", "Anh", "0365446686", ()),
    ("Ms. Anh 0963995886", "Anh", "0963995886", ()),
    ("Ms, Huệ 097 227 3064", "Huệ", "0972273064", ()),
    ("Mr. Hằng - 0973448092", "Hằng", "0973448092", ()),
    ("Đầo Mai - 033 863 2357", "Đầo Mai", "0338632357", ()),
    ("Annh Dũng 0945031111", "Dũng", "0945031111", ()),
    ("Mrs Long 0984695779", "Long", "0984695779", ()),
    # Two people on one line, separated by a slash.
    (
        "Chị Loan 0983280816/ Ngọc 0973319660",
        "Loan",
        "0983280816",
        ("Ngọc - 0973319660",),
    ),
    # Landline first, named contact on the next line.
    ("(024) 3853 2294\nChị Hoa: 0868327760", "Hoa", "0868327760", ("02438532294",)),
    ("(024) 3758 9975\nc Tuyến: 0936311119", "Tuyến", "0936311119", ("02437589975",)),
    # Branch labels.
    (
        "SR 1: Ms. Thoa 0972 173 867\nSR 2: Ms. Nghĩa 0988 406 555",
        "Thoa",
        "0972173867",
        ("Nghĩa - 0988406555",),
    ),
    # Two phones and no name at all.
    ("02253 591 335 - 0929 853 969", "", "02253591335", ("0929853969",)),
    ("(0222) 3821 128\n 0936 599 559", "", "02223821128", ("0936599559",)),
    ("0222 655 5678\n 0972502323", "", "02226555678", ("0972502323",)),
    # Only a hotline / only a number.
    ("Hotline: 0917 632 211", "", "0917632211", ()),
    ("0243 7911067", "", "02437911067", ()),
    # Number first, name in parentheses.
    ("0965687202 (Ms. Phương)", "Phương", "0965687202", ()),
    ("0898282095 (Mrs. Hải Anh)", "Hải Anh", "0898282095", ()),
]


@pytest.mark.parametrize(("raw", "name", "phone", "extras"), REFERENCE_CASES)
def test_reference_file_cases(raw, name, phone, extras):
    parsed = parse_contact(raw)
    assert parsed.primary_name == name
    assert parsed.primary_phone == phone
    assert parsed.extras == extras


def test_keeps_the_raw_cell_for_traceability():
    raw = "Chị Loan 0983280816/ Ngọc 0973319660"
    assert parse_contact(raw).raw == raw


def test_inline_newlines_survive_as_separators():
    parsed = parse_contact("Ms. Huyền\n0855004460")
    assert (parsed.primary_name, parsed.primary_phone) == ("Huyền", "0855004460")


def test_hyphen_inside_a_number_is_not_a_separator():
    """'0972 173-867' must stay one phone number, not become two fragments."""
    parsed = parse_contact("Ms. Thoa 0972 173-867")
    assert parsed.primary_phone == "0972173867"


def test_three_people_keep_two_extras():
    parsed = parse_contact(
        "Ms. A 0911111111 / Ms. B 0922222222 / Ms. C 0933333333"
    )
    assert (parsed.primary_name, parsed.primary_phone) == ("A", "0911111111")
    assert parsed.extras == ("B - 0922222222", "C - 0933333333")


def test_duplicate_numbers_are_not_repeated_in_extras():
    parsed = parse_contact("Chị Hương: 0949988999 / 0949988999")
    assert parsed.extras == ()


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_empty_cells_produce_no_contact(raw):
    parsed = parse_contact(raw)
    assert parsed.has_primary is False
    assert parsed.all_entries == ()


def test_name_only_cell_keeps_the_name_but_has_no_phone():
    parsed = parse_contact("Chị Hoa")
    assert parsed.primary_name == "Hoa"
    assert parsed.primary_phone == ""


def test_format_extra_contacts_joins_with_semicolons():
    assert format_extra_contacts(("Ngọc - 0973319660", "0987654321")) == (
        "Ngọc - 0973319660; 0987654321"
    )


# ---------------------------------------------------------------------------
# parse_sender — người gửi giữ nguyên danh xưng
# ---------------------------------------------------------------------------


def test_parse_sender_keeps_the_honorific():
    parsed = parse_sender("Mr Hải")
    assert parsed.primary_name == "Mr Hải"
    assert parsed.primary_phone == ""


def test_parse_sender_splits_name_and_phone_but_keeps_the_label():
    parsed = parse_sender("Mr Hải: 0392492229")
    assert parsed.primary_name == "Mr Hải"
    assert parsed.primary_phone == "0392492229"


def test_parse_sender_keeps_a_company_name_intact():
    parsed = parse_sender("Công ty CP Hoàng Nam - 0243 7911067")
    assert parsed.primary_name == "Công ty CP Hoàng Nam"
    assert parsed.primary_phone == "02437911067"


@pytest.mark.parametrize("raw", [None, "", "   "])
def test_parse_sender_on_empty_cell(raw):
    parsed = parse_sender(raw)
    assert parsed.primary_name == ""
    assert parsed.primary_phone == ""
