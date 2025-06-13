# database/config.py
from typing import Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus
_base_config=SettingsConfigDict(
        env_file="/Users/hemantkumar/Developer/backend/Fastapi-backend/.env",  # ✅ make sure .env is in root or adjust path
        env_ignore_empty=True,
        extra="ignore"
    )
class DatabaseSettings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: str
    # ✅ Properly encode password for safe URL construction
    @property
    def POSTGRES_URL(self) -> str:
        password_encoded = quote_plus(self.POSTGRES_PASSWORD)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{password_encoded}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = _base_config
class SecuritySettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config=_base_config
class NotificationSettings(BaseSettings):
    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_FROM_NAME:str
    MAIL_SERVER:str
    MAIL_PORT:int
    MAIL_STARTTLS:bool=True
    MAIL_SSL_TLS:bool=False
    USE_CREDENTIALS:bool=True
    VALIDATE_CERTS: bool = True
    model_config = _base_config
# ✅ Exported settings object to use elsewhere
db_settings = DatabaseSettings()
security_settings = SecuritySettings()
notification_settings= NotificationSettings()
print("🔍 Loaded Notification Settings from .env:", NotificationSettings().model_dump())
