"""Unit tests for the dashboard response schemas."""

from datetime import UTC, date, datetime
from decimal import Decimal

from app.schemas.dashboard import (
    DashboardDailyPoint,
    DashboardDestination,
    DashboardKpis,
    DashboardRange,
    DashboardSummary,
)


def test_money_serializes_as_string():
    kpis = DashboardKpis(
        total_bills=10,
        bills_today=1,
        in_progress_bills=3,
        delivered_bills=5,
        cancelled_bills=1,
        returned_bills=1,
        delivery_rate=50.0,
        revenue_total=Decimal("125000000.00"),
        revenue_today=Decimal("4500000.00"),
        cod_total=Decimal("32000000.00"),
    )
    data = kpis.model_dump(mode="json")
    assert data["revenue_total"] == "125000000.00"
    assert data["cod_total"] == "32000000.00"
    assert data["delivery_rate"] == 50.0


def test_dates_serialize_as_iso_strings():
    point = DashboardDailyPoint(date=date(2026, 11, 6), bills=2, revenue=Decimal("0.00"))
    assert point.model_dump(mode="json")["date"] == "2026-11-06"

    window = DashboardRange(days=30, date_from=date(2026, 10, 8), date_to=date(2026, 11, 6))
    assert window.model_dump(mode="json")["date_from"] == "2026-10-08"


def test_summary_round_trips_zero_filled_lists():
    summary = DashboardSummary(
        generated_at=datetime(2026, 11, 6, 8, 5, 0, tzinfo=UTC),
        range=DashboardRange(days=7, date_from=date(2026, 10, 31), date_to=date(2026, 11, 6)),
        kpis=DashboardKpis(
            total_bills=0,
            bills_today=0,
            in_progress_bills=0,
            delivered_bills=0,
            cancelled_bills=0,
            returned_bills=0,
            delivery_rate=0.0,
            revenue_total=Decimal("0.00"),
            revenue_today=Decimal("0.00"),
            cod_total=Decimal("0.00"),
        ),
        daily=[],
        status_counts=[],
        destinations=[DashboardDestination(province_code="1", province_name="Hà Nội", count=0)],
    )
    data = summary.model_dump(mode="json")
    assert data["kpis"]["total_bills"] == 0
    assert data["destinations"][0]["count"] == 0
    assert data["generated_at"].endswith("Z")
