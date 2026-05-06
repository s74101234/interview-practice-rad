from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    gemini_api_key: str
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    class Config:
        env_file = str(_ENV_FILE)


settings = Settings()
