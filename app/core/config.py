from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    gemini_model_name: str = Field("gemini-2.5-flash", alias="GEMINI_MODEL_NAME")
    google_maps_api_key: str = Field(..., alias="GEMINI_API_KEY")
    # Google Cloud
    google_application_credentials: str = Field(..., alias="GOOGLE_APPLICATION_CREDENTIALS")

    # App
    debug: bool = Field(False, alias="DEBUG")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Upload policy
    max_file_size_mb: int = Field(10, alias="MAX_FILE_SIZE_MB")
    allowed_mime_types: list[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"],
        alias="ALLOWED_MIME_TYPES"
    )
    disallowed_mime_types: list[str] = Field(default=["image/svg+xml"], alias="DISALLOWED_MIME_TYPES")
    ocr_concurrency: int = Field(4, alias="OCR_CONCURRENCY")
settings = Settings()