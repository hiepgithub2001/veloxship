# Feature: bills, Property: Filter AND composition (status + created date range)
"""
Property: Bill filter AND composition

For any combination of status, created_from, and created_to filters applied
simultaneously, every bill in the result set SHALL satisfy ALL applied filter
conditions (matching status AND created_at >= created_from AND created_at <= created_to).

**Validates: FR-013**
"""

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Domain constants ---
STATUSES = ["created", "picked_up", "in_transit", "delivered", "returned", "cancelled"]
TS_MIN = 1_500_000_000  # ~2017
TS_MAX = 1_800_000_000  # ~2027

bill_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "created_at": st.integers(min_value=TS_MIN, max_value=TS_MAX),
    }
)

timestamp_filter = st.one_of(st.none(), st.integers(min_value=TS_MIN, max_value=TS_MAX))


# --- Pure filter function (mirrors CRUD AND logic) ---
def apply_bill_filters(
    bills: list[dict],
    *,
    status: str | None = None,
    created_from: int | None = None,
    created_to: int | None = None,
) -> list[dict]:
    """Apply AND filters on a list of bill dicts, same logic as crud.list_bills."""
    result = bills
    if status:
        result = [b for b in result if b["status"] == status]
    if created_from is not None:
        result = [b for b in result if b["created_at"] >= created_from]
    if created_to is not None:
        result = [b for b in result if b["created_at"] <= created_to]
    return result


@settings(max_examples=200)
@given(
    bills=st.lists(bill_strategy, min_size=0, max_size=50),
    filter_status=st.one_of(st.none(), st.sampled_from(STATUSES)),
    filter_created_from=timestamp_filter,
    filter_created_to=timestamp_filter,
)
def test_filter_and_composition(
    bills: list[dict],
    filter_status: str | None,
    filter_created_from: int | None,
    filter_created_to: int | None,
) -> None:
    """Every returned bill satisfies ALL active filter conditions."""
    result = apply_bill_filters(
        bills,
        status=filter_status,
        created_from=filter_created_from,
        created_to=filter_created_to,
    )

    for b in result:
        if filter_status:
            assert b["status"] == filter_status, (
                f"Bill {b} does not match status filter '{filter_status}'"
            )
        if filter_created_from is not None:
            assert b["created_at"] >= filter_created_from, (
                f"Bill {b} is before created_from '{filter_created_from}'"
            )
        if filter_created_to is not None:
            assert b["created_at"] <= filter_created_to, (
                f"Bill {b} is after created_to '{filter_created_to}'"
            )


@settings(max_examples=200)
@given(
    bills=st.lists(bill_strategy, min_size=1, max_size=50),
    filter_status=st.one_of(st.none(), st.sampled_from(STATUSES)),
    filter_created_from=timestamp_filter,
    filter_created_to=timestamp_filter,
)
def test_filter_and_composition_no_false_exclusion(
    bills: list[dict],
    filter_status: str | None,
    filter_created_from: int | None,
    filter_created_to: int | None,
) -> None:
    """No bill that matches ALL conditions is excluded from the result set."""
    result = apply_bill_filters(
        bills,
        status=filter_status,
        created_from=filter_created_from,
        created_to=filter_created_to,
    )

    for b in bills:
        matches_all = True
        if filter_status and b["status"] != filter_status:
            matches_all = False
        if filter_created_from is not None and b["created_at"] < filter_created_from:
            matches_all = False
        if filter_created_to is not None and b["created_at"] > filter_created_to:
            matches_all = False

        if matches_all:
            assert b in result, f"Bill {b} matches all filters but is not in result"


@settings(max_examples=200)
@given(bills=st.lists(bill_strategy, min_size=0, max_size=50))
def test_no_filter_returns_all(bills: list[dict]) -> None:
    """When no filters are applied, all bills are returned."""
    result = apply_bill_filters(bills)
    assert result == bills
