from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_path: str = "data/orders.db"
    user_service_url: str = "http://user-service:8080"
    notification_service_url: str = "http://notification-service:8080"
    request_timeout: float = 2.0
    retry_attempts: int = 3
    retry_wait: float = 1.0
    breaker_threshold: int = 3
    breaker_timeout: float = 15.0


@lru_cache
def get_settings():
    return Settings()
