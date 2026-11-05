"""Unit tests for workbook layout detection and row reading."""

from io import BytesIO
from pathlib import Path

import pytest
from openpyxl import Workbook

from app.services.importing.readers import (
    RowLimitExceeded,
    detect_layout,
    iter_raw_rows,
    load_workbook_from_bytes,
)

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "import-mr-hai-logex.xlsx"

LEGACY_HEADER = [
    "Mã đơn",
    "Tiền tố",
    "Mã đơn",
    "Địa điểm giao",
    "Tên đại lý nhận",
    "Địa chỉ giao chi tiết",
    "Liên hệ",
    "Số lượng Catalogue",
    "Số kiện",
    "Trọng lượng (kg)",
]


def _synthetic_workbook() -> bytes:
    """Recreate the awkward parts of the real file, including the duplicate header."""
    workbook = Workbook()
    workbook.active.title = "Sheet1"  # deliberately empty, like the real file
    sheet = workbook.create_sheet("Du lieu")
    sheet.append(["HNB - MINI CATALOGUE 2H.2026"])
    sheet.append(LEGACY_HEADER)
    sheet.append(
        [5, "HNLG", "=B3&A3", "Hà Nội", "HẰNG HÒA", "Địa chỉ A", "Chị Hương: 0949988999", 150, 3, 43.5]
    )
    sheet.append([None] * 10)
    sheet.append(
        [9, "HNLG", "=B5&A5", "Hải Dương", "HIỀN HUỆ", "Địa chỉ B", "Em Kiên: 0961357756", 100, 2, 29]
    )
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def test_detects_the_data_sheet_and_skips_the_empty_one():
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    detection = detect_layout(workbook)
    assert detection.found
    assert detection.sheet_name == "Du lieu"
    assert detection.header_row == 2


def test_two_tracking_columns_use_the_rightmost_as_the_full_code():
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    columns = detect_layout(workbook).columns
    assert columns["tracking_serial"] == 0
    assert columns["tracking"] == 2


def test_every_required_field_is_mapped():
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    columns = detect_layout(workbook).columns
    for field in ("tracking", "destination", "receiver_name", "contact", "packages", "weight"):
        assert field in columns


def test_rows_below_the_header_are_read_and_blank_rows_skipped():
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    layout = detect_layout(workbook).layout
    rows = iter_raw_rows(workbook, layout)
    assert [row.row_number for row in rows] == [3, 5]


def test_formula_cell_without_a_cached_value_reads_as_none():
    """The importer must fall back to prefix + serial when Excel stored no cache."""
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    layout = detect_layout(workbook).layout
    first = iter_raw_rows(workbook, layout)[0]
    assert first.cells["tracking"] is None
    assert first.cells["tracking_prefix"] == "HNLG"
    assert first.cells["tracking_serial"] == 5


def test_row_limit_is_enforced():
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    layout = detect_layout(workbook).layout
    with pytest.raises(RowLimitExceeded):
        iter_raw_rows(workbook, layout, max_rows=1)


def test_real_fixture_is_detected_and_fully_read():
    assert FIXTURE.exists(), "golden fixture missing"
    workbook = load_workbook_from_bytes(FIXTURE.read_bytes())
    detection = detect_layout(workbook)
    assert detection.found
    assert detection.sheet_name == "Sheet2"  # Sheet1 is empty in the real file
    assert detection.header_row == 2

    rows = iter_raw_rows(workbook, detection.layout)
    assert len(rows) == 70
    assert rows[0].row_number == 3
    assert rows[-1].row_number == 72
    # Cached formula value is available in an Excel-saved file.
    assert rows[0].cells["tracking"] == "HNLG5"
    assert rows[-1].cells["tracking"] == "HNLG0-GT"


def test_workbook_without_the_expected_columns_reports_what_is_missing():
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Mã đơn", "Tên khách hàng"])
    worksheet.append(["X1", "Ai đó"])
    buffer = BytesIO()
    workbook.save(buffer)
    detection = detect_layout(load_workbook_from_bytes(buffer.getvalue()))
    assert detection.found is False
    assert "weight" in detection.missing
    assert "contact" in detection.missing


def test_sender_columns_are_detected_when_present():
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(LEGACY_HEADER + ["Người gửi", "SĐT người gửi"])
    sheet.append(
        [5, "HNLG", "HNLG5", "Hà Nội", "HẰNG HÒA", "Địa chỉ A",
         "Chị Hương: 0949988999", 150, 3, 43.5, "Mr Hải", "0392492229"]
    )
    buffer = BytesIO()
    workbook.save(buffer)

    opened = load_workbook_from_bytes(buffer.getvalue())
    detection = detect_layout(opened)
    assert detection.found
    assert "sender" in detection.columns
    assert "sender_phone" in detection.columns

    row = iter_raw_rows(opened, detection.layout)[0]
    assert row.cells["sender"] == "Mr Hải"
    assert row.cells["sender_phone"] == "0392492229"


def test_rows_without_sender_columns_still_validate():
    """Sender is optional: the legacy 10-column file must keep working."""
    workbook = load_workbook_from_bytes(_synthetic_workbook())
    detection = detect_layout(workbook)
    assert detection.found
    assert "sender" not in detection.columns
