from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    EARTHDATA_USER: str | None = Field(None, env="EARTHDATA_USER")
    EARTHDATA_PASS: str | None = Field(None, env="EARTHDATA_PASS")
    AIRNOW_API_KEY: str | None = Field(None, env="AIRNOW_API_KEY")
    OPENWEATHER_API_KEY: str | None = Field(None, env="OPENWEATHER_API_KEY")
    TEMPO_DAILY_HOUR: int = 2
    AIRNOW_INTERVAL_MINUTES: int = 30
    OPENWEATHER_INTERVAL_MINUTES: int = 30
    ml_model_dir: Path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
