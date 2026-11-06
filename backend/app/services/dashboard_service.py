"""Dashboard business logic — compose aggregate queries into a summary.

The API layer stays thin. Every rule lives here: the VN-day window, zero-filling
of the daily series and status/destination buckets, the delivery-rate formula,
and Decimal money quantisation.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import dashboard as dashboard_crud
from app.crud import location as location_crud
from app.schemas.bill import BillStatus
from app.schemas.dashboard import (
    DashboardDailyPoint,
    DashboardDestination,
    DashboardKpis,
    DashboardRange,
    DashboardStatusCount,
    DashboardSummary,
)
from app.services.importing.locations import PROVINCES

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
STATUS_ORDER = [status.value for status in BillStatus]
_MONEY_PLACES = Decimal("0.01")
_PREFIX_RE = re.compile(r"^(Thành phố|Tỉnh)\s+", re.IGNORECASE)

#: Synthetic bucket for bills whose snapshot province code no longer exists in
#: the post-2025 34-province layout. Shown in the bar list but never on the map.
OTHER_PROVINCE_CODE = "__other__"


def vn_day_bounds(
    days: int, now: datetime | None = None
) -> tuple[date, date, datetime, datetime]:
    """Return ``(start_date, today, start_utc, end_utc)`` for a ``days`` window.

    ``today`` is derived in ``Asia/Ho_Chi_Minh``; the UTC bounds are naive UTC to
    match how ``bills.created_at`` is stored.
    """
    current = (now or datetime.now(VN_TZ)).astimezone(VN_TZ)
    today = current.date()
    start_date = today - timedelta(days=days - 1)
    start_utc = datetime.combine(start_date, time.min, tzinfo=VN_TZ).astimezone(UTC)
    end_utc = datetime.combine(today + timedelta(days=1), time.min, tzinfo=VN_TZ).astimezone(UTC)
    return start_date, today, start_utc.replace(tzinfo=None), end_utc.replace(tzinfo=None)


def delivery_rate(delivered: int, total: int) -> float:
    """Return the delivery rate (0-100, one decimal), 0.0 when there are no bills."""
    if total <= 0:
        return 0.0
    return round(delivered / total * 100, 1)


def build_daily_series(
    rows: list[tuple[date, int, Decimal]], start_date: date, end_date: date
) -> list[dict]:
    """Zero-fill the daily series across ``[start_date, end_date]`` (inclusive)."""
    by_date = {day: (bills, revenue) for day, bills, revenue in rows}
    result: list[dict] = []
    cursor = start_date
    while cursor <= end_date:
        bills, revenue = by_date.get(cursor, (0, Decimal("0.00")))
        result.append(
            {
                "date": cursor,
                "bills": bills,
                "revenue": _money(revenue),
            }
        )
        cursor += timedelta(days=1)
    return result


def _display_name(name: str) -> str:
    """Strip the ``Tỉnh`` / ``Thành phố`` prefix for chart-friendly labels."""
    return _PREFIX_RE.sub("", (name or "").strip())


def build_destinations(
    rows: dict[str, int], provinces: list[tuple[str, str]]
) -> list[dict]:
    """Zero-fill every known province and fold unknown codes into an ``Khác`` bucket."""
    known_codes = {code for code, _ in provinces}
    items: list[dict] = [
        {
            "province_code": code,
            "province_name": _display_name(name),
            "count": rows.get(code, 0),
        }
        for code, name in provinces
    ]
    other = sum(count for code, count in rows.items() if code not in known_codes)
    if other:
        items.append(
            {"province_code": OTHER_PROVINCE_CODE, "province_name": "Khác", "count": other}
        )
    items.sort(key=lambda item: (-item["count"], item["province_name"]))
    return items


def _money(value: object) -> Decimal:
    """Coerce an aggregate money value to a 2-decimal ``Decimal``."""
    if isinstance(value, Decimal):
        return value.quantize(_MONEY_PLACES)
    return Decimal(str(value)).quantize(_MONEY_PLACES)


async def _load_provinces(db: AsyncSession) -> list[tuple[str, str]]:
    """Return ``(code, name)`` for every province, preferring the DB rows."""
    province_rows = await location_crud.list_provinces(db)
    if province_rows:
        return [(p.code, p.name) for p in province_rows]
    return list(PROVINCES)


async def get_summary(db: AsyncSession, days: int) -> DashboardSummary:
    """Build the complete dashboard summary for the given period."""
    start_date, today, start_utc, end_utc = vn_day_bounds(days)

    totals = await dashboard_crud.fetch_totals(db, start_utc, end_utc)
    daily_rows = await dashboard_crud.fetch_daily(db, start_utc, end_utc)
    status_raw = await dashboard_crud.fetch_status_counts(db, start_utc, end_utc)
    destination_raw = await dashboard_crud.fetch_destinations(db, start_utc, end_utc)

    daily = build_daily_series(daily_rows, start_date, today)
    today_point = daily[-1]

    provinces = await _load_provinces(db)

    kpis = DashboardKpis(
        total_bills=totals["total_bills"],
        bills_today=today_point["bills"],
        in_progress_bills=totals["in_progress_bills"],
        delivered_bills=totals["delivered_bills"],
        cancelled_bills=totals["cancelled_bills"],
        returned_bills=totals["returned_bills"],
        delivery_rate=delivery_rate(totals["delivered_bills"], totals["total_bills"]),
        revenue_total=_money(totals["revenue_total"]),
        revenue_today=_money(today_point["revenue"]),
        cod_total=_money(totals["cod_total"]),
    )

    return DashboardSummary(
        generated_at=datetime.now(UTC),
        range=DashboardRange(days=days, date_from=start_date, date_to=today),
        kpis=kpis,
        daily=[DashboardDailyPoint(**point) for point in daily],
        status_counts=[
            DashboardStatusCount(status=status, count=status_raw.get(status, 0))
            for status in STATUS_ORDER
        ],
        destinations=[
            DashboardDestination(**item)
            for item in build_destinations(destination_raw, provinces)
        ],
    )
