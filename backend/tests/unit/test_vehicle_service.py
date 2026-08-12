"""Unit tests for app.services.vehicle_service — create & update flows."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.services.vehicle_service import create_vehicle, update_vehicle


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _make_vehicle(**overrides):
    """Build a fake Vehicle object with sensible defaults."""
    defaults = {
        "id": 1,
        "license_plate": "51C-12345",
        "vehicle_type": "truck",
        "max_weight_kg": Decimal("5000.000"),
        "max_volume_m3": Decimal("20.50"),
        "driver_id": None,
        "latest_depot_id": None,
        "status": "active",
        "created_at": datetime(2024, 1, 15, 10, 0, 0),
        "updated_at": datetime(2024, 1, 15, 10, 0, 0),
    }
    defaults.update(overrides)
    vehicle = MagicMock()
    for k, v in defaults.items():
        setattr(vehicle, k, v)
    return vehicle


def _mock_db_execute_result(scalar_value):
    """Create an AsyncMock that mimics db.execute() returning a result with scalar_one_or_none."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = scalar_value
    return result


# ─── create_vehicle tests ────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestCreateVehicle:
    """Tests for create_vehicle service function."""

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_duplicate_license_plate_raises_conflict_error(self, mock_crud):
        """ConflictError raised when license_plate already exists."""
        db = AsyncMock()
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=_make_vehicle())

        payload = VehicleCreate(
            license_plate="51C-12345",
            vehicle_type="truck",
            max_weight_kg=Decimal("5000"),
            max_volume_m3=Decimal("20"),
        )

        with pytest.raises(ConflictError) as exc_info:
            await create_vehicle(db, payload)

        assert exc_info.value.error_code == "LICENSE_PLATE_EXISTS"

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_invalid_driver_id_raises_app_error(self, mock_crud):
        """AppError with DRIVER_NOT_FOUND when driver_id references no active user."""
        db = AsyncMock()
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        # db.execute returns result where scalar_one_or_none is None (no active user)
        db.execute = AsyncMock(return_value=_mock_db_execute_result(None))

        payload = VehicleCreate(
            license_plate="51C-99999",
            vehicle_type="motorcycle",
            max_weight_kg=Decimal("200"),
            max_volume_m3=Decimal("1.5"),
            driver_id=999,
        )

        with pytest.raises(AppError) as exc_info:
            await create_vehicle(db, payload)

        assert exc_info.value.error_code == "DRIVER_NOT_FOUND"
        assert exc_info.value.status_code == 422

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_invalid_depot_id_raises_app_error(self, mock_crud):
        """AppError with DEPOT_NOT_FOUND when latest_depot_id references no depot."""
        db = AsyncMock()
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        # First call for driver validation passes, second call for depot validation fails
        db.execute = AsyncMock(return_value=_mock_db_execute_result(None))

        payload = VehicleCreate(
            license_plate="51C-88888",
            vehicle_type="truck",
            max_weight_kg=Decimal("3000"),
            max_volume_m3=Decimal("15"),
            latest_depot_id=999,
        )

        with pytest.raises(AppError) as exc_info:
            await create_vehicle(db, payload)

        assert exc_info.value.error_code == "DEPOT_NOT_FOUND"
        assert exc_info.value.status_code == 422

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_successful_create(self, mock_crud):
        """Successful vehicle creation delegates to CRUD and returns the vehicle."""
        db = AsyncMock()
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        created_vehicle = _make_vehicle(license_plate="51C-77777")
        mock_crud.create_vehicle = AsyncMock(return_value=created_vehicle)

        payload = VehicleCreate(
            license_plate="51C-77777",
            vehicle_type="truck",
            max_weight_kg=Decimal("5000"),
            max_volume_m3=Decimal("20"),
        )

        result = await create_vehicle(db, payload)

        assert result == created_vehicle
        mock_crud.create_vehicle.assert_called_once()

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_create_with_driver_and_depot_validated(self, mock_crud):
        """Successful creation when driver_id and latest_depot_id exist."""
        db = AsyncMock()
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        # Both driver and depot validations pass (scalar returns a value)
        db.execute = AsyncMock(return_value=_mock_db_execute_result(1))

        created_vehicle = _make_vehicle(driver_id=3, latest_depot_id=1)
        mock_crud.create_vehicle = AsyncMock(return_value=created_vehicle)

        payload = VehicleCreate(
            license_plate="51C-66666",
            vehicle_type="motorcycle",
            max_weight_kg=Decimal("200"),
            max_volume_m3=Decimal("1.5"),
            driver_id=3,
            latest_depot_id=1,
        )

        result = await create_vehicle(db, payload)

        assert result == created_vehicle
        assert db.execute.call_count == 2  # driver + depot validation


# ─── update_vehicle tests ────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestUpdateVehicle:
    """Tests for update_vehicle service function."""

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_vehicle_not_found_raises_not_found_error(self, mock_crud):
        """NotFoundError raised when vehicle_id doesn't exist."""
        db = AsyncMock()
        mock_crud.get_vehicle = AsyncMock(return_value=None)

        payload = VehicleUpdate(license_plate="51C-99999")

        with pytest.raises(NotFoundError) as exc_info:
            await update_vehicle(db, 999, payload)

        assert exc_info.value.error_code == "VEHICLE_NOT_FOUND"

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_duplicate_license_plate_on_update_raises_conflict_error(self, mock_crud):
        """ConflictError raised when updating to an existing license_plate owned by another vehicle."""
        db = AsyncMock()
        existing_vehicle = _make_vehicle(id=1, license_plate="51C-12345")
        mock_crud.get_vehicle = AsyncMock(return_value=existing_vehicle)

        # Another vehicle already owns the target plate
        other_vehicle = _make_vehicle(id=2, license_plate="51C-99999")
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=other_vehicle)

        payload = VehicleUpdate(license_plate="51C-99999")

        with pytest.raises(ConflictError) as exc_info:
            await update_vehicle(db, 1, payload)

        assert exc_info.value.error_code == "LICENSE_PLATE_EXISTS"

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_invalid_driver_id_on_update_raises_app_error(self, mock_crud):
        """AppError with DRIVER_NOT_FOUND when updating with invalid driver_id."""
        db = AsyncMock()
        existing_vehicle = _make_vehicle(id=1)
        mock_crud.get_vehicle = AsyncMock(return_value=existing_vehicle)
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        # Driver validation fails
        db.execute = AsyncMock(return_value=_mock_db_execute_result(None))

        payload = VehicleUpdate(driver_id=999)

        with pytest.raises(AppError) as exc_info:
            await update_vehicle(db, 1, payload)

        assert exc_info.value.error_code == "DRIVER_NOT_FOUND"

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_invalid_depot_id_on_update_raises_app_error(self, mock_crud):
        """AppError with DEPOT_NOT_FOUND when updating with invalid latest_depot_id."""
        db = AsyncMock()
        existing_vehicle = _make_vehicle(id=1)
        mock_crud.get_vehicle = AsyncMock(return_value=existing_vehicle)

        # Depot validation fails
        db.execute = AsyncMock(return_value=_mock_db_execute_result(None))

        payload = VehicleUpdate(latest_depot_id=999)

        with pytest.raises(AppError) as exc_info:
            await update_vehicle(db, 1, payload)

        assert exc_info.value.error_code == "DEPOT_NOT_FOUND"

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_status_idempotency_returns_vehicle_unchanged(self, mock_crud):
        """When setting same status with no other fields, vehicle is returned as-is (no CRUD update)."""
        db = AsyncMock()
        existing_vehicle = _make_vehicle(id=1, status="active")
        mock_crud.get_vehicle = AsyncMock(return_value=existing_vehicle)

        payload = VehicleUpdate(status="active")

        result = await update_vehicle(db, 1, payload)

        assert result == existing_vehicle
        # update_vehicle CRUD should NOT be called
        mock_crud.update_vehicle.assert_not_called()

    @patch("app.services.vehicle_service.vehicle_crud")
    async def test_successful_update(self, mock_crud):
        """Successful update delegates to CRUD and returns updated vehicle."""
        db = AsyncMock()
        existing_vehicle = _make_vehicle(id=1, status="active")
        mock_crud.get_vehicle = AsyncMock(return_value=existing_vehicle)
        mock_crud.get_vehicle_by_license_plate = AsyncMock(return_value=None)

        updated_vehicle = _make_vehicle(id=1, status="inactive")
        mock_crud.update_vehicle = AsyncMock(return_value=updated_vehicle)

        payload = VehicleUpdate(status="inactive")

        result = await update_vehicle(db, 1, payload)

        assert result == updated_vehicle
        mock_crud.update_vehicle.assert_called_once()
