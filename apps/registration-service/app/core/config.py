from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Registration Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    KAFKA_TOPIC_REGISTRATIONS: str = "event.registrations"
    KAFKA_TOPIC_RESULTS: str = "event.registration.results"

settings = Settings()