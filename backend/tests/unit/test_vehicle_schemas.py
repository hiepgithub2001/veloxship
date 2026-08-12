"""Unit tests for vehicle schemas validation."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.vehicle import VehicleCreate, VehicleUpdate


# ---------------------------------------------------------------------------
# VehicleCreate tests
# ---------------------------------------------------------------------------


class TestVehicleCreateLicensePlate:
    """Test license_plate validation on VehicleCreate."""

    def test_valid_license_plate(self):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type="motorcycle",
            max_weight_kg=Decimal("100"),
            max_volume_m3=Decimal("1.5"),
        )
        assert schema.license_plate == "51F-123.45"

    def test_empty_license_plate_rejected(self):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="",
                vehicle_type="motorcycle",
                max_weight_kg=Decimal("100"),
                max_volume_m3=Decimal("1.5"),
            )

    def test_whitespace_only_license_plate_rejected(self):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="   ",
                vehicle_type="motorcycle",
                max_weight_kg=Decimal("100"),
                max_volume_m3=Decimal("1.5"),
            )


class TestVehicleCreateVehicleType:
    """Test vehicle_type validation on VehicleCreate."""

    @pytest.mark.parametrize("vtype", ["motorcycle", "truck"])
    def test_valid_vehicle_types(self, vtype: str):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type=vtype,
            max_weight_kg=Decimal("100"),
            max_volume_m3=Decimal("1.5"),
        )
        assert schema.vehicle_type == vtype

    @pytest.mark.parametrize("vtype", ["car", "van", "bicycle", ""])
    def test_invalid_vehicle_types_rejected(self, vtype: str):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="51F-123.45",
                vehicle_type=vtype,
                max_weight_kg=Decimal("100"),
                max_volume_m3=Decimal("1.5"),
            )


class TestVehicleCreateWeight:
    """Test max_weight_kg validation on VehicleCreate."""

    def test_positive_weight_accepted(self):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type="truck",
            max_weight_kg=Decimal("500"),
            max_volume_m3=Decimal("2.0"),
        )
        assert schema.max_weight_kg == Decimal("500")

    @pytest.mark.parametrize("weight", [Decimal("0"), Decimal("-1")])
    def test_zero_or_negative_weight_rejected(self, weight: Decimal):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="51F-123.45",
                vehicle_type="truck",
                max_weight_kg=weight,
                max_volume_m3=Decimal("2.0"),
            )


class TestVehicleCreateVolume:
    """Test max_volume_m3 validation on VehicleCreate."""

    def test_positive_volume_accepted(self):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type="truck",
            max_weight_kg=Decimal("500"),
            max_volume_m3=Decimal("3.5"),
        )
        assert schema.max_volume_m3 == Decimal("3.5")

    @pytest.mark.parametrize("volume", [Decimal("0"), Decimal("-2.5")])
    def test_zero_or_negative_volume_rejected(self, volume: Decimal):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="51F-123.45",
                vehicle_type="truck",
                max_weight_kg=Decimal("500"),
                max_volume_m3=volume,
            )


class TestVehicleCreateStatus:
    """Test status validation on VehicleCreate."""

    @pytest.mark.parametrize("status", ["active", "inactive", "maintenance"])
    def test_valid_statuses(self, status: str):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type="motorcycle",
            max_weight_kg=Decimal("100"),
            max_volume_m3=Decimal("1.0"),
            status=status,
        )
        assert schema.status == status

    def test_none_status_accepted(self):
        schema = VehicleCreate(
            license_plate="51F-123.45",
            vehicle_type="motorcycle",
            max_weight_kg=Decimal("100"),
            max_volume_m3=Decimal("1.0"),
        )
        assert schema.status is None

    @pytest.mark.parametrize("status", ["deleted", "suspended", ""])
    def test_invalid_statuses_rejected(self, status: str):
        with pytest.raises(ValidationError):
            VehicleCreate(
                license_plate="51F-123.45",
                vehicle_type="motorcycle",
                max_weight_kg=Decimal("100"),
                max_volume_m3=Decimal("1.0"),
                status=status,
            )


# ---------------------------------------------------------------------------
# VehicleUpdate tests
# ---------------------------------------------------------------------------


class TestVehicleUpdateLicensePlate:
    """Test license_plate validation on VehicleUpdate."""

    def test_valid_license_plate(self):
        schema = VehicleUpdate(license_plate="30A-999.99")
        assert schema.license_plate == "30A-999.99"

    def test_none_license_plate_accepted(self):
        schema = VehicleUpdate()
        assert schema.license_plate is None

    def test_empty_license_plate_rejected(self):
        with pytest.raises(ValidationError):
            VehicleUpdate(license_plate="")

    def test_whitespace_only_license_plate_rejected(self):
        with pytest.raises(ValidationError):
            VehicleUpdate(license_plate="  ")


class TestVehicleUpdateVehicleType:
    """Test vehicle_type validation on VehicleUpdate."""

    @pytest.mark.parametrize("vtype", ["motorcycle", "truck"])
    def test_valid_vehicle_types(self, vtype: str):
        schema = VehicleUpdate(vehicle_type=vtype)
        assert schema.vehicle_type == vtype

    def test_none_vehicle_type_accepted(self):
        schema = VehicleUpdate()
        assert schema.vehicle_type is None

    @pytest.mark.parametrize("vtype", ["car", "bus"])
    def test_invalid_vehicle_types_rejected(self, vtype: str):
        with pytest.raises(ValidationError):
            VehicleUpdate(vehicle_type=vtype)


class TestVehicleUpdateWeight:
    """Test max_weight_kg validation on VehicleUpdate."""

    def test_positive_weight_accepted(self):
        schema = VehicleUpdate(max_weight_kg=Decimal("200"))
        assert schema.max_weight_kg == Decimal("200")

    def test_none_weight_accepted(self):
        schema = VehicleUpdate()
        assert schema.max_weight_kg is None

    @pytest.mark.parametrize("weight", [Decimal("0"), Decimal("-5")])
    def test_zero_or_negative_weight_rejected(self, weight: Decimal):
        with pytest.raises(ValidationError):
            VehicleUpdate(max_weight_kg=weight)


class TestVehicleUpdateVolume:
    """Test max_volume_m3 validation on VehicleUpdate."""

    def test_positive_volume_accepted(self):
        schema = VehicleUpdate(max_volume_m3=Decimal("4.0"))
        assert schema.max_volume_m3 == Decimal("4.0")

    def test_none_volume_accepted(self):
        schema = VehicleUpdate()
        assert schema.max_volume_m3 is None

    @pytest.mark.parametrize("volume", [Decimal("0"), Decimal("-1.5")])
    def test_zero_or_negative_volume_rejected(self, volume: Decimal):
        with pytest.raises(ValidationError):
            VehicleUpdate(max_volume_m3=volume)


class TestVehicleUpdateStatus:
    """Test status validation on VehicleUpdate."""

    @pytest.mark.parametrize("status", ["active", "inactive", "maintenance"])
    def test_valid_statuses(self, status: str):
        schema = VehicleUpdate(status=status)
        assert schema.status == status

    def test_none_status_accepted(self):
        schema = VehicleUpdate()
        assert schema.status is None

    @pytest.mark.parametrize("status", ["deleted", "unknown"])
    def test_invalid_statuses_rejected(self, status: str):
        with pytest.raises(ValidationError):
            VehicleUpdate(status=status)
