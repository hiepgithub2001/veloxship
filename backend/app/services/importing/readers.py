"""Locate the data table inside an uploaded workbook and stream its rows.

The importer never assumes a fixed sheet name or a fixed header row: it scans
the first rows of every worksheet, picks the one that matches the most known
column headers, and then reads from the row below it.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from io import BytesIO
from typing import Any

from openpyxl import load_workbook

from app.services.importing.normalize import normalize_key
from app.services.importing.template import (
    HEADER_LOOKUP,
    PREFIX_ALIASES,
    REQUIRED_FIELDS,
    TRACKING_ALIASES,
)

MAX_HEADER_SCAN_ROWS = 10


class RowLimitExceeded(Exception):
    """Raised when the workbook holds more data rows than the configured cap."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"row limit exceeded: {limit}")


@dataclass(frozen=True)
class DetectedLayout:
    """Where the data table lives and which column holds which field."""

    sheet_name: str
    header_row: int
    columns: dict[str, int]


@dataclass(frozen=True)
class LayoutDetection:
    """Result of scanning a workbook for a usable table."""

    layout: DetectedLayout | None = None
    sheet_name: str | None = None
    header_row: int | None = None
    columns: dict[str, int] = field(default_factory=dict)
    missing: tuple[str, ...] = ()

    @property
    def found(self) -> bool:
        return self.layout is not None and not self.missing


@dataclass(frozen=True)
class RawRow:
    """One spreadsheet row, keyed by logical field."""

    row_number: int
    cells: dict[str, Any]
    values: tuple[Any, ...] = ()


def load_workbook_from_bytes(data: bytes):
    """Open a workbook read-only, using cached values for formula cells.

    ``data_only=True`` is what turns the ``=B3&A3`` formula in the tracking
    column into ``HNLG5``.
    """
    return load_workbook(BytesIO(data), read_only=True, data_only=True)


def _match_header(values: tuple[Any, ...]) -> dict[str, int]:
    """Map logical field -> 0-based column index for one candidate header row."""
    tracking_columns: list[int] = []
    prefix_column: int | None = None
    columns: dict[str, int] = {}

    for index, value in enumerate(values):
        key = normalize_key(value)
        if not key:
            continue
        if key in TRACKING_ALIASES:
            tracking_columns.append(index)
            continue
        if key in PREFIX_ALIASES:
            if prefix_column is None:
                prefix_column = index
            continue
        field_name = HEADER_LOOKUP.get(key)
        if field_name and field_name not in columns:
            columns[field_name] = index

    # A file may repeat the "Mã đơn" header (number column + full-code column).
    # The rightmost one is the complete code; the leftmost is its serial part,
    # kept as a fallback when the formula cell has no cached value.
    if len(tracking_columns) >= 2:
        columns["tracking_serial"] = tracking_columns[0]
        columns["tracking"] = tracking_columns[-1]
    elif tracking_columns:
        columns["tracking"] = tracking_columns[0]

    if prefix_column is not None:
        columns["tracking_prefix"] = prefix_column
    return columns


def detect_layout(workbook) -> LayoutDetection:
    """Scan every sheet and return the best-matching data table."""
    best: LayoutDetection | None = None
    best_score = -1

    for worksheet in workbook.worksheets:
        rows: Iterator[tuple[Any, ...]] = worksheet.iter_rows(
            min_row=1, max_row=MAX_HEADER_SCAN_ROWS, values_only=True
        )
        for row_number, row_values in enumerate(rows, start=1):
            columns = _match_header(tuple(row_values))
            score = sum(1 for name in REQUIRED_FIELDS if name in columns)
            if score <= best_score:
                continue
            missing = tuple(name for name in REQUIRED_FIELDS if name not in columns)
            best_score = score
            best = LayoutDetection(
                layout=(
                    DetectedLayout(worksheet.title, row_number, columns)
                    if not missing
                    else None
                ),
                sheet_name=worksheet.title,
                header_row=row_number,
                columns=columns,
                missing=missing,
            )

    return best or LayoutDetection(missing=REQUIRED_FIELDS)


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    return isinstance(value, str) and not value.strip()


def iter_raw_rows(
    workbook,
    layout: DetectedLayout,
    *,
    max_rows: int = 5000,
) -> list[RawRow]:
    """Read every non-empty data row below the header row."""
    worksheet = workbook[layout.sheet_name]
    rows: list[RawRow] = []

    for row_number, values in enumerate(
        worksheet.iter_rows(min_row=layout.header_row + 1, values_only=True),
        start=layout.header_row + 1,
    ):
        cells = {
            name: (values[index] if index < len(values) else None)
            for name, index in layout.columns.items()
        }
        if all(_is_blank(value) for value in cells.values()):
            continue
        rows.append(RawRow(row_number=row_number, cells=cells, values=tuple(values)))
        if len(rows) > max_rows:
            raise RowLimitExceeded(max_rows)

    return rows
