"""Unit tests for user (staff) schema validation."""

import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserUpdate


class TestUserCreate:
    """Test UserCreate validation."""

    def test_valid_create(self):
        schema = UserCreate(username="nvquay01", full_name="Nguyễn Văn A", phone="0901234567")
        assert schema.username == "nvquay01"
        assert schema.role == "operator"

    def test_username_is_normalized_to_lowercase(self):
        schema = UserCreate(username="  NVQuay01 ", full_name="Nguyễn Văn A")
        assert schema.username == "nvquay01"

    def test_short_username_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="ab", full_name="Nguyễn Văn A")

    def test_username_with_space_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="has space", full_name="Nguyễn Văn A")

    def test_invalid_phone_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="nvquay01", full_name="Nguyễn Văn A", phone="123")

    def test_empty_role_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="nvquay01", full_name="Nguyễn Văn A", role="   ")

    def test_short_password_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="nvquay01", full_name="Nguyễn Văn A", password="123")


class TestUserUpdate:
    """Test UserUpdate (partial) validation."""

    def test_empty_update_accepted(self):
        schema = UserUpdate()
        assert schema.role is None

    def test_empty_role_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(role="   ")

    def test_invalid_phone_rejected(self):
        with pytest.raises(ValidationError):
            UserUpdate(phone="abc")
