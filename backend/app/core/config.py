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

    # Customer code
    CUSTOMER_CODE_PREFIX: str = "KH"

    # Carrier branding (used in print template)
    CARRIER_NAME: str = "Vận Chuyển Hoàng Nam"
    CARRIER_HOTLINE: str = "0989784688"
    CARRIER_WEBSITE: str = ""
    CARRIER_EMAIL: str = "Tranthuyduong01051986@gmail.com"
    BILL_PDF_COPY_COUNT: int = 3

    # AWS S3 storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = ""
    AWS_REGION: str = "ap-southeast-1"
    UPLOAD_MAX_SIZE_BYTES: int = 20 * 1024 * 1024  # 20 MB
    UPLOAD_PREFIX: str = "uploads/"
    S3_PRESIGNED_URL_EXPIRES_IN: int = 3600

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
