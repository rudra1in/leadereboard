from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    """
    Externalized configuration – perfect for Kubernetes ConfigMap + env vars.
    """
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    bootstrap_servers: str = Field(default="localhost:9092")
    client_id: Optional[str] = None

    # Security
    security_protocol: str = "PLAINTEXT"
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None

    # Producer tuning (2.15 recommended defaults)
    acks: str = "all"
    enable_idempotence: bool = True
    retries: int = 5
    compression_type: str = "snappy"
    linger_ms: int = 5
    batch_size: int = 16384
    request_timeout_ms: int = 30000

    def to_confluent_config(self) -> Dict[str, Any]:
        conf = {
            "bootstrap.servers": self.bootstrap_servers,
            "client.id": self.client_id or "unknown-service",
            "acks": self.acks,
            "enable.idempotence": self.enable_idempotence,
            "retries": self.retries,
            "compression.type": self.compression_type,
            "linger.ms": self.linger_ms,
            "batch.size": self.batch_size,
            "request.timeout.ms": self.request_timeout_ms,
        }

        if self.security_protocol.upper() != "PLAINTEXT":
            conf["security.protocol"] = self.security_protocol
            if self.sasl_mechanism:
                conf["sasl.mechanism"] = self.sasl_mechanism
                conf["sasl.username"] = self.sasl_username
                conf["sasl.password"] = self.sasl_password

        return conf