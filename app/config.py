from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경변수 설정을 관리합니다."""

    # MongoDB
    MONGO_URL: str = "mongodb://babdongmu:babdongmu1234@localhost:27017"
    MONGO_DB: str = "babdongmu"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CoolSMS (선택)
    COOLSMS_API_KEY: str = ""
    COOLSMS_API_SECRET: str = ""
    COOLSMS_SENDER: str = ""

    # OpenAI (AI 요약 기능)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"


settings = Settings()
