from typing import Optional, Dict, Any
from .config import KafkaSettings
from .template import KafkaTemplate


class KafkaTemplateFactory:
    @staticmethod
    def create(
        client_id: Optional[str] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> KafkaTemplate:
        """
        Create KafkaTemplate with optional overrides.
        Priority: overrides > env/ConfigMap > defaults
        """
        data = KafkaSettings().model_dump()

        if client_id:
            data["client_id"] = client_id
        if overrides:
            data.update(overrides)

        settings = KafkaSettings(**data)
        return KafkaTemplate(settings)