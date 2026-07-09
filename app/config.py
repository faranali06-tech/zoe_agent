from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "prod"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./app.db"

    VAPI_WEBHOOK_BEARER: str = ""

    LLM_PROVIDER: str = "none"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    OAUTH_REDIRECT_BASE_URL: str = ""
    PUBLIC_BASE_URL: str = ""

    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    TIKTOK_CLIENT_ID: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    INSTAGRAM_CLIENT_ID: str = ""
    INSTAGRAM_CLIENT_SECRET: str = ""

    BOSS_PHONE_NUMBER_E164: str = "+966551846135"
    VAPI_PRIVATE_API_KEY: str = ""
    VAPI_ASSISTANT_ID_ZOE: str = "b849fdf5-e367-49dc-ae33-c863788c7819"
    VAPI_PHONE_NUMBER_ID_TWILIO: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
