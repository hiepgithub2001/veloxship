"""Unit tests for the storage router."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer valid.token"}


@pytest.fixture
def mock_token_decode():
    with patch("app.api.v1.deps.decode_token") as m:
        m.return_value = {"sub": "1", "type": "access"}
        yield m


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = 1
    user.username = "tester"
    user.role = "admin"
    return user


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture(autouse=True)
def override_deps(mock_token_decode, mock_user, mock_db_session):
    from app.api.v1.deps import get_db, get_current_user
    from app.db.session import session_factory

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield
    app.dependency_overrides.clear()


class TestUploadEndpoint:
    @patch("app.api.v1.storage.upload_file")
    def test_upload_returns_201(self, mock_upload_call, auth_headers):
        mock_upload_call.return_value = MagicMock(
            model_dump=lambda: {
                "key": "uploads/abc123_test.jpg",
                "mime_type": "image/jpeg",
                "size_bytes": 51200,
                "ext": "jpeg",
                "public_url": None,
            }
        )
        response = client.post(
            "/api/v1/storage/upload",
            files={"file": ("photo.jpg", b"\xff\xd8\xff\xe0", "image/jpeg")},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["ext"] == "jpeg"
