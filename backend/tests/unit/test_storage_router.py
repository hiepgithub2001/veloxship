"""Unit tests for the storage router."""

from __future__ import annotations

from contextlib import asynccontextmanager
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
    from app.db.session import async_session_factory

    app.dependency_overrides.clear()
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield
    app.dependency_overrides.clear()


from app.schemas.storage import UploadResultResponse
from app.services.storage_service import upload_file


class TestUploadPipelineDependency:
    @pytest.mark.asyncio
    async def test_upload_pipeline_success(self):
        file = MagicMock()
        file.filename = "test.jpg"
        file.size = 100
        file.read = AsyncMock(return_value=b"\xff\xd8\xff\xe0\x00\x10JFIF")
        file.seek = AsyncMock()
        file.file = MagicMock()

        mock_s3_client = MagicMock()
        mock_s3_client.upload_fileobj = AsyncMock()

        @asynccontextmanager
        async def mock_get_s3_client():
            yield mock_s3_client

        with patch(
            "app.services.storage.get_s3_client", side_effect=mock_get_s3_client
        ):
            with patch("app.services.storage.validators.validate_file") as mock_val:
                mock_val.return_value = MagicMock(
                    file=file,
                    safe_filename="test.jpg",
                    ext="jpg",
                    mime_type="image/jpeg",
                    size=100,
                )
                res = await upload_file(file)
                assert isinstance(res, UploadResultResponse)
                assert res.mime_type == "image/jpeg"
                assert res.ext == "jpg"
                mock_s3_client.upload_fileobj.assert_called_once()

    def test_file_upload_endpoint_returns_201(self, auth_headers):
        mock_s3_client = MagicMock()
        mock_s3_client.upload_fileobj = AsyncMock()

        @asynccontextmanager
        async def mock_get_s3_client():
            yield mock_s3_client

        with patch(
            "app.services.storage.get_s3_client", side_effect=mock_get_s3_client
        ):
            response = client.post(
                "/api/v1/files/upload",
                files={
                    "file": ("photo.jpg", b"\xff\xd8\xff\xe0\x00\x10JFIF", "image/jpeg")
                },
                headers=auth_headers,
            )
            assert response.status_code == status.HTTP_201_CREATED
            body = response.json()
            assert body["mime_type"] == "image/jpeg"
            assert "key" in body
