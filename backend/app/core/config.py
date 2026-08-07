"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Strongly-typed settings read from .env / environment."""

    # Database
    DATABASE_URL: str  # Required — must be set via .env or environment

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MINUTES: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7

    # Tracking number
    TRACKING_NUMBER_PREFIX: str = "NL"

    # Carrier branding (used in print template)
    CARRIER_NAME: str = "Vận Chuyển HN"
    CARRIER_HOTLINE: str = "0972 160 610"
    CARRIER_WEBSITE: str = "newlinks.vn"
    CARRIER_EMAIL: str = "info@newlinks.vn"

    # Cloudflare R2 storage
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_REGION: str = "auto"
    R2_ENDPOINT_URL: str = ""
    UPLOAD_MAX_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    UPLOAD_PREFIX: str = "uploads/"
    R2_PUBLIC_BASE_URL: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
