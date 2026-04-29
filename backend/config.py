from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = ""
    REDIS_URL: str = "redis://redis:6379/0"
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000
    DATABASE_URL: str = "sqlite:////app/data/sap_mock.db"
    MOCK_MODE: bool = True
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
