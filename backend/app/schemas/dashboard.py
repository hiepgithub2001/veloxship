"""Dashboard schemas — the aggregated summary returned by ``GET /dashboard/summary``.

Money values use ``Decimal``, which Pydantic serializes as a JSON string (the
same convention as ``CustomerMetrics``) — callers must parse rather than rely on
float coercion. All counts and time buckets are computed on the creation date of
the bill (a creation cohort), in the ``Asia/Ho_Chi_Minh`` timezone.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class DashboardRange(BaseModel):
    """The inclusive VN date window the summary covers."""

    days: int
    date_from: date
    date_to: date


class DashboardKpis(BaseModel):
    """Headline figures for the selected period."""

    total_bills: int
    bills_today: int
    in_progress_bills: int
    delivered_bills: int
    cancelled_bills: int
    returned_bills: int
    delivery_rate: float
    revenue_total: Decimal
    revenue_today: Decimal
    cod_total: Decimal


class DashboardDailyPoint(BaseModel):
    """One day in the zero-filled daily series."""

    date: date
    bills: int
    revenue: Decimal


class DashboardStatusCount(BaseModel):
    """Count of bills in one lifecycle status."""

    status: str
    count: int


class DashboardDestination(BaseModel):
    """Bill volume per destination province (zero-filled across all provinces)."""

    province_code: str
    province_name: str
    count: int


class DashboardSummary(BaseModel):
    """Complete dashboard payload for one period."""

    generated_at: datetime
    range: DashboardRange
    kpis: DashboardKpis
    daily: list[DashboardDailyPoint]
    status_counts: list[DashboardStatusCount]
    destinations: list[DashboardDestination]
