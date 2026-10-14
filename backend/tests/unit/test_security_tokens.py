"""Unit tests for the JWT token helpers in `app.core.security`.

Pins down the claims the refresh flow depends on: the `type` discriminator must
differ between access and refresh tokens, and each token must carry its own TTL.
No database required.
"""

from datetime import UTC, datetime, timedelta

import pytest
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token


def _expires_in(token: str) -> float:
    """Seconds from now until the token's `exp`."""
    claims = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return claims["exp"] - datetime.now(UTC).timestamp()


class TestAccessToken:
    def test_carries_the_access_type_and_subject(self):
        token = create_access_token(42, "nvquay01")
        claims = decode_token(token)

        assert claims["type"] == "access"
        assert claims["sub"] == "42"
        assert claims["username"] == "nvquay01"

    def test_uses_the_configured_access_ttl(self):
        token = create_access_token(42, "nvquay01")
        expected = settings.ACCESS_TOKEN_TTL_MINUTES * 60
        # Allow a couple of seconds of clock drift during the call.
        assert abs(_expires_in(token) - expected) < 5


class TestRefreshToken:
    def test_carries_the_refresh_type(self):
        token = create_refresh_token(42, "nvquay01")
        claims = decode_token(token)

        assert claims["type"] == "refresh"
        assert claims["sub"] == "42"

    def test_uses_the_configured_refresh_ttl(self):
        token = create_refresh_token(42, "nvquay01")
        expected = settings.REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60
        assert abs(_expires_in(token) - expected) < 5

    def test_is_distinguishable_from_an_access_token(self):
        """The refresh endpoint relies on `type` to reject access tokens."""
        access = decode_token(create_access_token(1, "u"))
        refresh = decode_token(create_refresh_token(1, "u"))
        assert access["type"] != refresh["type"]


class TestTokenUniqueness:
    def test_tokens_minted_in_the_same_second_still_differ(self):
        """Refresh rotation must not hand back the token it is replacing.

        JWT encoding is deterministic, so without a unique `jti` two tokens with
        the same claims and the same second-precision `exp` would be identical.
        """
        first = create_refresh_token(7, "nvquay01")
        second = create_refresh_token(7, "nvquay01")

        assert first != second
        assert decode_token(first)["jti"] != decode_token(second)["jti"]

    def test_every_token_carries_a_jti(self):
        assert decode_token(create_access_token(1, "u"))["jti"]
        assert decode_token(create_refresh_token(1, "u"))["jti"]


class TestDecodeToken:
    def test_rejects_a_token_signed_with_another_secret(self):
        forged = jwt.encode({"sub": "1", "type": "refresh"}, "other-secret", algorithm="HS256")
        with pytest.raises(JWTError):
            decode_token(forged)

    def test_rejects_an_expired_token(self):
        expired = jwt.encode(
            {
                "sub": "1",
                "type": "refresh",
                "exp": datetime.now(UTC) - timedelta(seconds=1),
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        with pytest.raises(JWTError):
            decode_token(expired)

    def test_rejects_garbage(self):
        with pytest.raises(JWTError):
            decode_token("not-a-jwt")
