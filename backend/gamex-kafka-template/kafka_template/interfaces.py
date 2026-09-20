from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class KafkaProducerInterface(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def send(
        self,
        topic: str,
        value: Any,
        key: Optional[Union[str, bytes]] = None,
        headers: Optional[list[tuple[str, bytes]]] = None,
        partition: Optional[int] = None,
    ) -> None: ...

    @abstractmethod
    async def send_async(
        self,
        topic: str,
        value: Any,
        key: Optional[Union[str, bytes]] = None,
    ): ...