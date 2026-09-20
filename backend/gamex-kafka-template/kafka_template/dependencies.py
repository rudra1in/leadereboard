from typing import Annotated
from fastapi import Request, Depends
from .interfaces import KafkaProducerInterface


def get_kafka_template(request: Request) -> KafkaProducerInterface:
    template = getattr(request.app.state, "kafka_template", None)
    if template is None:
        raise RuntimeError("KafkaTemplate not initialized in lifespan")
    return template


KafkaTemplateDep = Annotated[KafkaProducerInterface, Depends(get_kafka_template)]