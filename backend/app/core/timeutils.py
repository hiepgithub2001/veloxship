"""Datetime helpers shared by API query filters.

Database timestamps (`bills.created_at`, `customers.created_at`, …) are stored
as naive UTC, while clients send ISO-8601 strings that may carry an offset.
Filters therefore have to normalize before comparing.
"""

from datetime import UTC, datetime


def naive_utc(dt: datetime | None) -> datetime | None:
    """Normalize a filter timestamp to naive UTC, matching DB column storage."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).replace(tzinfo=None)
