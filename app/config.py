from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """환경변수 설정을 관리합니다."""

    # DB: 로컬은 SQLite, Docker 배포 시 PostgreSQL URL로 교체
    DATABASE_URL: str = "sqlite+aiosqlite:///./babdongmu.db"

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Solapi(=CoolSMS) (SMS 발송)
    SOLAPI_API_KEY: str = ""
    SOLAPI_API_SECRET: str = ""
    SOLAPI_SENDER: str = ""

    # Gemini (AI 요약 기능)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
