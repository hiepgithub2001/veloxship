"""Unit tests for the per-row rule engine."""

from typing import Any

import pytest

from app.services.importing.readers import RawRow
from app.services.importing.validators import (
    ERROR_DUPLICATE_TRACKING,
    ERROR_NUMBER,
    ERROR_PACKAGES,
    ERROR_PHONE,
    ERROR_PROVINCE,
    ERROR_REQUIRED,
    ERROR_TRACKING,
    ERROR_WEIGHT,
    STATUS_ERROR,
    STATUS_OK,
    STATUS_WARNING,
    ValidationContext,
    validate_row,
)

BASE_CELLS: dict[str, Any] = {
    "tracking": "HNLG5",
    "destination": "Hà Nội",
    "receiver_name": "HẰNG HÒA",
    "address": "B2 10 Shop house 24H Đường Tố Hữu, Phường Hà Đông, Hà Nội.",
    "contact": "Chị Hương: 0949988999",
    "catalogue_qty": 150,
    "packages": 3,
    "weight": 43.5,
}


def _row(**overrides) -> RawRow:
    cells = dict(BASE_CELLS)
    for key, value in overrides.items():
        if value is None:
            cells.pop(key, None)
        else:
            cells[key] = value
    return RawRow(row_number=3, cells=cells)


def _validate(**overrides) -> Any:
    return validate_row(_row(**overrides))


def test_happy_row_normalises_every_field():
    result = _validate()
    assert result.status == STATUS_OK
    assert result.error_code is None
    normalized = result.normalized
    assert normalized["tracking_number"] == "HNLG5"
    assert normalized["province_code"] == "1"
    assert normalized["province_name"] == "Hà Nội"
    assert normalized["destination_raw"] == "Hà Nội"
    assert normalized["receiver_name"] == "HẰNG HÒA"
    assert normalized["contact_name"] == "Hương"
    assert normalized["contact_phone"] == "0949988999"
    assert normalized["packages"] == 3
    assert normalized["weight_kg"] == "43.500"
    assert normalized["catalogue_quantity"] == 150


def test_tracking_falls_back_to_prefix_plus_serial():
    """When the formula cell has no cached value, B + A must still produce the code."""
    result = _validate(tracking=None, tracking_prefix="HNLG", tracking_serial=5)
    assert result.status == STATUS_OK
    assert result.normalized["tracking_number"] == "HNLG5"


def test_weight_float_noise_is_quantised():
    result = _validate(weight=28.999999999999996)
    assert result.normalized["weight_kg"] == "29.000"


def test_missing_tracking_is_an_error():
    result = _validate(tracking=None)
    assert result.status == STATUS_ERROR
    assert result.error_code == ERROR_REQUIRED


def test_tracking_with_spaces_is_rejected():
    result = _validate(tracking="HNLG 5")
    assert result.status == STATUS_ERROR
    assert result.error_code == ERROR_TRACKING


def test_tracking_longer_than_fifty_characters_is_rejected():
    result = _validate(tracking="A" * 51)
    assert result.error_code == ERROR_TRACKING


def test_unknown_province_reports_suggestions():
    result = _validate(destination="Hà Nội 2")
    assert result.status == STATUS_ERROR
    assert result.error_code == ERROR_PROVINCE
    assert "Hà Nội" in result.error_message


def test_merged_province_is_resolved_with_a_warning():
    result = _validate(destination="Hải Dương")
    assert result.status == STATUS_WARNING
    assert result.normalized["province_name"] == "Hải Phòng"
    assert result.normalized["destination_raw"] == "Hải Dương"
    assert any("Hải Phòng" in warning for warning in result.warnings)


def test_internal_office_warns_but_still_imports():
    result = _validate(destination="Chi Nhánh HN")
    assert result.status == STATUS_WARNING
    assert result.normalized["province_name"] == "Hà Nội"


def test_missing_receiver_name_is_an_error():
    result = _validate(receiver_name=None)
    assert result.error_code == ERROR_REQUIRED


def test_missing_contact_cell_is_an_error():
    result = _validate(contact=None)
    assert result.error_code == ERROR_REQUIRED


def test_contact_without_a_phone_is_an_error():
    result = _validate(contact="Chỉ có tên không có số")
    assert result.status == STATUS_ERROR
    assert result.error_code == ERROR_PHONE


def test_second_contact_produces_an_extra_entry():
    result = _validate(contact="Chị Loan 0983280816/ Ngọc 0973319660")
    assert result.normalized["extra_contacts"] == ["Ngọc - 0973319660"]
    assert any("bình luận" in warning for warning in result.warnings)


def test_blank_packages_fall_back_to_the_default():
    result = _validate(packages=None)
    assert result.status == STATUS_WARNING
    assert result.normalized["packages"] == 1


def test_zero_packages_is_an_error():
    result = _validate(packages=0)
    assert result.error_code == ERROR_PACKAGES


def test_non_numeric_packages_is_an_error():
    result = _validate(packages="ba kiện")
    assert result.error_code == ERROR_NUMBER


def test_zero_weight_is_an_error():
    result = _validate(weight=0)
    assert result.error_code == ERROR_WEIGHT


def test_missing_weight_is_an_error():
    result = _validate(weight=None)
    assert result.error_code == ERROR_WEIGHT


def test_unreadable_catalogue_quantity_is_dropped_with_a_warning():
    result = _validate(catalogue_qty="nhiều")
    assert result.status == STATUS_WARNING
    assert "catalogue_quantity" not in result.normalized


def test_negative_catalogue_quantity_is_dropped_with_a_warning():
    result = _validate(catalogue_qty=-5)
    assert "catalogue_quantity" not in result.normalized
    assert result.status == STATUS_WARNING


@pytest.mark.parametrize("existing", ["HNLG5", "hnlg5".upper()])
def test_existing_tracking_number_is_flagged_for_skipping(existing):
    context = ValidationContext(existing_tracking=frozenset({existing}))
    result = validate_row(_row(), context)
    assert result.status == STATUS_WARNING
    assert result.error_code == ERROR_DUPLICATE_TRACKING
    assert result.is_skipped_on_commit is True
    assert result.is_usable is True


def test_error_rows_are_not_usable():
    result = _validate(destination="Xứ sở thần tiên")
    assert result.is_usable is False


def test_address_is_kept_verbatim():
    address = "  Số 7,  lô 4A, khu đô thị Trung Yên "
    result = _validate(address=address)
    assert result.normalized["address_detail"] == "Số 7, lô 4A, khu đô thị Trung Yên"


def test_missing_address_is_allowed():
    result = _validate(address=None)
    assert result.status == STATUS_OK
    assert result.normalized["address_detail"] == ""


def test_normalize_names_option_title_cases_upper_case_names():
    from app.services.importing.template import ImportOptions

    context = ValidationContext(options=ImportOptions(normalize_names=True))
    result = validate_row(_row(receiver_name="HẰNG HÒA"), context)
    assert result.normalized["receiver_name"] == "Hằng Hòa"


# ---------------------------------------------------------------------------
# Người gửi (tuỳ chọn)
# ---------------------------------------------------------------------------


def test_sender_parsed_from_a_combined_cell_keeps_the_honorific():
    result = _validate(sender="Mr Hải: 0392492229")
    assert result.normalized["sender_name"] == "Mr Hải"
    assert result.normalized["sender_phone"] == "0392492229"


def test_separate_sender_phone_column_wins_over_the_parsed_phone():
    result = _validate(sender="Mr Hải: 0900000000", sender_phone="0392 492 229")
    assert result.normalized["sender_name"] == "Mr Hải"
    assert result.normalized["sender_phone"] == "0392492229"


def test_sender_falls_back_to_the_import_option():
    from app.services.importing.template import ImportOptions

    context = ValidationContext(
        options=ImportOptions(sender_name="Mr Hải", sender_phone="0392492229")
    )
    result = validate_row(_row(), context)
    assert result.normalized["sender_name"] == "Mr Hải"
    assert result.normalized["sender_phone"] == "0392492229"


def test_sender_column_wins_over_the_import_option():
    from app.services.importing.template import ImportOptions

    context = ValidationContext(
        options=ImportOptions(sender_name="Công ty", sender_phone="0900000000")
    )
    result = validate_row(_row(sender="Mr Hải: 0392492229"), context)
    assert result.normalized["sender_name"] == "Mr Hải"
    assert result.normalized["sender_phone"] == "0392492229"


def test_unreadable_sender_phone_warns_but_keeps_the_row_usable():
    result = _validate(sender="Mr Hải")
    assert result.status == STATUS_WARNING
    assert result.is_usable is True
    assert result.normalized["sender_name"] == "Mr Hải"
    # The key may be present but empty — the service then falls back to settings.
    assert not result.normalized.get("sender_phone")
    assert any("người gửi" in warning for warning in result.warnings)


def test_invalid_sender_phone_option_warns():
    from app.services.importing.template import ImportOptions

    context = ValidationContext(options=ImportOptions(sender_phone="abc"))
    result = validate_row(_row(), context)
    assert "sender_phone" not in result.normalized
    assert any("tuỳ chọn" in warning for warning in result.warnings)


def test_no_sender_anywhere_leaves_the_keys_out():
    result = _validate()
    assert "sender_name" not in result.normalized
    assert "sender_phone" not in result.normalized
