from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_expires_min: int = 4320
    redis_url: str

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.1-chat-latest"

settings = Settings()
