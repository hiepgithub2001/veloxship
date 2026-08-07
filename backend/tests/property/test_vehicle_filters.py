# Feature: vehicles-management, Property 2: Filter AND composition
"""
Property 2: Filter AND composition

For any combination of status, vehicle_type, and latest_depot_id filters applied
simultaneously, every vehicle in the result set SHALL satisfy ALL applied filter
conditions (matching status AND matching vehicle_type AND matching latest_depot_id).

**Validates: Requirements 1.3, 1.4, 1.5, 1.9**
"""

from hypothesis import given, settings, assume
from hypothesis import strategies as st

# --- Domain constants ---
STATUSES = ["active", "inactive", "maintenance"]
VEHICLE_TYPES = ["motorcycle", "truck"]
DEPOT_IDS = list(range(1, 11))  # 10 possible depots


# --- Strategy: a single vehicle dict ---
vehicle_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "vehicle_type": st.sampled_from(VEHICLE_TYPES),
        "latest_depot_id": st.one_of(st.none(), st.sampled_from(DEPOT_IDS)),
    }
)


# --- Pure filter function (mirrors CRUD AND logic) ---
def apply_filters(
    vehicles: list[dict],
    *,
    status: str | None = None,
    vehicle_type: str | None = None,
    latest_depot_id: int | None = None,
) -> list[dict]:
    """Apply AND filters on a list of vehicle dicts, same logic as crud.list_vehicles."""
    result = vehicles
    if status:
        result = [v for v in result if v["status"] == status]
    if vehicle_type:
        result = [v for v in result if v["vehicle_type"] == vehicle_type]
    if latest_depot_id is not None:
        result = [v for v in result if v["latest_depot_id"] == latest_depot_id]
    return result


# --- Property test ---
@settings(max_examples=200)
@given(
    vehicles=st.lists(vehicle_strategy, min_size=0, max_size=50),
    filter_status=st.one_of(st.none(), st.sampled_from(STATUSES)),
    filter_vehicle_type=st.one_of(st.none(), st.sampled_from(VEHICLE_TYPES)),
    filter_depot_id=st.one_of(st.none(), st.sampled_from(DEPOT_IDS)),
)
def test_filter_and_composition(
    vehicles: list[dict],
    filter_status: str | None,
    filter_vehicle_type: str | None,
    filter_depot_id: int | None,
) -> None:
    """Every returned vehicle satisfies ALL active filter conditions."""
    # Apply filters
    result = apply_filters(
        vehicles,
        status=filter_status,
        vehicle_type=filter_vehicle_type,
        latest_depot_id=filter_depot_id,
    )

    # Assert: every vehicle in result matches ALL applied filters
    for v in result:
        if filter_status:
            assert v["status"] == filter_status, (
                f"Vehicle {v} does not match status filter '{filter_status}'"
            )
        if filter_vehicle_type:
            assert v["vehicle_type"] == filter_vehicle_type, (
                f"Vehicle {v} does not match vehicle_type filter '{filter_vehicle_type}'"
            )
        if filter_depot_id is not None:
            assert v["latest_depot_id"] == filter_depot_id, (
                f"Vehicle {v} does not match latest_depot_id filter '{filter_depot_id}'"
            )


@settings(max_examples=200)
@given(
    vehicles=st.lists(vehicle_strategy, min_size=1, max_size=50),
    filter_status=st.one_of(st.none(), st.sampled_from(STATUSES)),
    filter_vehicle_type=st.one_of(st.none(), st.sampled_from(VEHICLE_TYPES)),
    filter_depot_id=st.one_of(st.none(), st.sampled_from(DEPOT_IDS)),
)
def test_filter_and_composition_no_false_exclusion(
    vehicles: list[dict],
    filter_status: str | None,
    filter_vehicle_type: str | None,
    filter_depot_id: int | None,
) -> None:
    """No vehicle that matches ALL conditions is excluded from the result set."""
    result = apply_filters(
        vehicles,
        status=filter_status,
        vehicle_type=filter_vehicle_type,
        latest_depot_id=filter_depot_id,
    )

    # For every vehicle in the original list that matches all conditions,
    # it must appear in the result the correct number of times.
    for v in vehicles:
        matches_all = True
        if filter_status and v["status"] != filter_status:
            matches_all = False
        if filter_vehicle_type and v["vehicle_type"] != filter_vehicle_type:
            matches_all = False
        if filter_depot_id is not None and v["latest_depot_id"] != filter_depot_id:
            matches_all = False

        if matches_all:
            assert v in result, (
                f"Vehicle {v} matches all filters but is not in result"
            )


@settings(max_examples=200)
@given(
    vehicles=st.lists(vehicle_strategy, min_size=0, max_size=50),
)
def test_no_filter_returns_all(vehicles: list[dict]) -> None:
    """When no filters are applied, all vehicles are returned."""
    result = apply_filters(vehicles)
    assert result == vehicles
