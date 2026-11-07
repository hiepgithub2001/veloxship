"""Unit tests for the dashboard aggregation helpers (pure functions)."""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from app.core.exceptions import AppError
from app.services.dashboard_service import (
    OTHER_PROVINCE_CODE,
    build_daily_series,
    build_destinations,
    date_range_bounds,
    delivery_rate,
    resolve_date_range,
    vn_day_bounds,
)

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def test_vn_day_bounds_single_day():
    now = datetime(2026, 11, 6, 10, 0, 0, tzinfo=VN_TZ)
    start_date, today, start_utc, end_utc = vn_day_bounds(1, now=now)

    assert start_date == date(2026, 11, 6)
    assert today == date(2026, 11, 6)
    # 00:00 VN == 17:00 UTC of the previous day, stored naive.
    assert start_utc == datetime(2026, 11, 5, 17, 0, 0)
    assert end_utc == datetime(2026, 11, 6, 17, 0, 0)


def test_vn_day_bounds_multi_day():
    now = datetime(2026, 11, 6, 23, 30, 0, tzinfo=VN_TZ)
    start_date, today, _, _ = vn_day_bounds(30, now=now)
    assert start_date == date(2026, 10, 8)
    assert today == date(2026, 11, 6)


def test_delivery_rate_rounds_to_one_decimal():
    assert delivery_rate(2, 3) == 66.7
    assert delivery_rate(80, 128) == 62.5


def test_resolve_date_range_defaults_to_last_30_days():
    now = datetime(2026, 11, 6, 10, 0, 0, tzinfo=VN_TZ)
    start, end = resolve_date_range(None, None, now=now)
    assert start == date(2026, 10, 8)
    assert end == date(2026, 11, 6)


def test_resolve_date_range_accepts_explicit_dates():
    start, end = resolve_date_range(date(2026, 10, 1), date(2026, 10, 31))
    assert (start, end) == (date(2026, 10, 1), date(2026, 10, 31))


def test_resolve_date_range_rejects_incomplete_bounds():
    with pytest.raises(AppError) as exc:
        resolve_date_range(date(2026, 10, 1), None)
    assert exc.value.error_code == "DATE_RANGE_INCOMPLETE"


def test_resolve_date_range_rejects_inverted_range():
    with pytest.raises(AppError) as exc:
        resolve_date_range(date(2026, 11, 6), date(2026, 11, 1))
    assert exc.value.error_code == "DATE_RANGE_INVALID"


def test_resolve_date_range_rejects_too_large_range():
    with pytest.raises(AppError) as exc:
        resolve_date_range(date(2025, 1, 1), date(2026, 11, 6))
    assert exc.value.error_code == "DATE_RANGE_TOO_LARGE"


def test_date_range_bounds_covers_inclusive_vn_days():
    start_utc, end_utc = date_range_bounds(date(2026, 11, 6), date(2026, 11, 6))
    assert start_utc == datetime(2026, 11, 5, 17, 0, 0)
    assert end_utc == datetime(2026, 11, 6, 17, 0, 0)


def test_delivery_rate_zero_total_is_zero():
    assert delivery_rate(0, 0) == 0.0
    assert delivery_rate(5, 0) == 0.0


def test_build_daily_series_zero_fills_gaps():
    rows = [
        (date(2026, 11, 5), 2, Decimal("1000.00")),
        (date(2026, 11, 6), 0, Decimal("0.00")),
    ]
    series = build_daily_series(rows, date(2026, 11, 4), date(2026, 11, 6))

    assert [point["date"] for point in series] == [
        date(2026, 11, 4),
        date(2026, 11, 5),
        date(2026, 11, 6),
    ]
    assert series[0]["bills"] == 0
    assert series[0]["revenue"] == Decimal("0.00")
    assert series[1]["bills"] == 2


def test_build_destinations_strips_prefix_and_zero_fills():
    provinces = [("1", "Thành phố Hà Nội"), ("79", "Thành phố Hồ Chí Minh")]
    rows = {"1": 3, "999": 2}

    items = build_destinations(rows, provinces)

    assert [item["province_code"] for item in items] == ["1", OTHER_PROVINCE_CODE, "79"]
    assert items[0] == {"province_code": "1", "province_name": "Hà Nội", "count": 3}
    assert items[1] == {"province_code": OTHER_PROVINCE_CODE, "province_name": "Khác", "count": 2}
    assert items[2] == {"province_code": "79", "province_name": "Hồ Chí Minh", "count": 0}


def test_build_destinations_omits_other_when_no_unknown_codes():
    provinces = [("1", "Thành phố Hà Nội")]
    items = build_destinations({"1": 4}, provinces)
    assert len(items) == 1
    assert items[0]["province_code"] == "1"
