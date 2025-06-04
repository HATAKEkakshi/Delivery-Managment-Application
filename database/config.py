# database/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus

class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # ✅ Properly encode password for safe URL construction
    @property
    def POSTGRES_URL(self) -> str:
        password_encoded = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{password_encoded}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file="./.env",  # ✅ make sure .env is in root or adjust path
        env_ignore_empty=True,
        extra="ignore"
    )

# ✅ Exported settings object to use elsewhere
settings = DatabaseSettings()
