from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    KAMIS_API_KEY: str = ""
    KAMIS_API_ID: str = ""
    KAMIS_BASE_URL: str = "https://www.kamis.or.kr/service/price/xml.do"
    GOOGLE_API_KEY: str = ""
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    FRONTEND_ORIGIN: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
