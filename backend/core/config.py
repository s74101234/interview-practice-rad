from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    class Config:
        env_file = ".env"


settings = Settings()
