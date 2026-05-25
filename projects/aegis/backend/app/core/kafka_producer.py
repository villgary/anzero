from aiokafka import AIOKafkaProducer
from typing import Any
import logging
import json

logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self, bootstrap_servers: list[str]):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()

    async def stop(self) -> None:
        if self.producer:
            await self.producer.stop()
            self.producer = None

    async def send(self, topic: str, event: dict[str, Any]) -> bool:
        try:
            if not self.producer:
                raise RuntimeError("Producer not started")
            await self.producer.send_and_wait(topic, event)
            return True
        except Exception as e:
            logger.error(f"Failed to send event to {topic}: {e}")
            raise
