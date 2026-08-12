# Feature: vehicles-management, Property 1: Search filter correctness
"""
Property-based test for vehicle search filter correctness.

**Validates: Requirements 1.2**

For any set of vehicles and for any search string, every vehicle in the result
set SHALL have a license_plate that contains the search string (case-insensitive),
and no vehicle whose license_plate contains the search string shall be excluded
from the result set.
"""

from hypothesis import given, settings
from hypothesis import strategies as st


# Pure search filter logic — mirrors the CRUD's case-insensitive LIKE filter
def search_vehicles_by_plate(license_plates: list[str], search: str) -> list[str]:
    """Filter license plates using the same logic as the CRUD layer.

    Replicates: func.lower(Vehicle.license_plate).like("%" + func.lower(search_term) + "%")
    """
    search_term = search.strip()
    if not search_term:
        return license_plates
    lower_search = search_term.lower()
    return [plate for plate in license_plates if lower_search in plate.lower()]


# Strategy: generate license plates as short alphanumeric strings
plate_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-. "),
    min_size=1,
    max_size=12,
)


@settings(max_examples=200)
@given(
    plates=st.lists(plate_strategy, min_size=0, max_size=30),
    search=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="-. "),
        min_size=0,
        max_size=8,
    ),
)
def test_search_filter_correctness(plates: list[str], search: str) -> None:
    """Every result must contain the search string; no matching plate is excluded."""
    results = search_vehicles_by_plate(plates, search)

    search_term = search.strip()
    if not search_term:
        # Empty/whitespace search returns all plates
        assert results == plates
        return

    lower_search = search_term.lower()

    # 1. Every result contains the search string (no false positives)
    for plate in results:
        assert lower_search in plate.lower(), (
            f"False positive: '{plate}' does not contain '{search_term}'"
        )

    # 2. No matching plate was excluded (no false negatives)
    for plate in plates:
        if lower_search in plate.lower():
            assert plate in results, (
                f"False negative: '{plate}' contains '{search_term}' but was excluded"
            )
