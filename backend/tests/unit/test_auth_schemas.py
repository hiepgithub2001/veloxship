"""Unit tests for self-service auth schemas (profile update, change password)."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import ChangePasswordRequest, ProfileUpdate


class TestProfileUpdate:
    """Test ProfileUpdate validation."""

    def test_empty_update_accepted(self):
        schema = ProfileUpdate()
        assert schema.full_name is None
        assert schema.phone is None
        assert schema.avatar is None

    def test_full_name_is_stripped(self):
        schema = ProfileUpdate(full_name="  Nguyễn Văn A  ")
        assert schema.full_name == "Nguyễn Văn A"

    def test_too_short_full_name_rejected(self):
        with pytest.raises(ValidationError):
            ProfileUpdate(full_name="")

    def test_valid_phone_accepted(self):
        schema = ProfileUpdate(phone="0901234567")
        assert schema.phone == "0901234567"

    def test_invalid_phone_rejected(self):
        with pytest.raises(ValidationError):
            ProfileUpdate(phone="12345")

    def test_avatar_accepts_key_or_none(self):
        assert ProfileUpdate(avatar="uploads/abc.png").avatar == "uploads/abc.png"
        assert ProfileUpdate(avatar=None).avatar is None


class TestChangePasswordRequest:
    """Test ChangePasswordRequest validation."""

    def test_valid_request(self):
        schema = ChangePasswordRequest(current_password="oldpass", new_password="newpass123")
        assert schema.new_password == "newpass123"

    def test_short_new_password_rejected(self):
        with pytest.raises(ValidationError):
            ChangePasswordRequest(current_password="oldpass", new_password="123")

    def test_missing_current_password_rejected(self):
        with pytest.raises(ValidationError):
            ChangePasswordRequest(new_password="newpass123")
