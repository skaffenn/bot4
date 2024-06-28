from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    openai_api_token: str
    assistant_id: str
    vector_store_id: str
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Settings()
