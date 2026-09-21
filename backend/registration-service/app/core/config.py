from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Registration Service"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@postgres-service.gamex.svc.cluster.local:5432/app"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8000/notify"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    KAFKA_TOPIC_REGISTRATIONS: str = "event.registrations"
    KAFKA_TOPIC_RESULTS: str = "event.registration.results"

settings = Settings()