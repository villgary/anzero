from aiokafka import AIOKafkaProducer
from typing import Any
import json

class KafkaProducer:
    def __init__(self, bootstrap_servers: list[str]):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic: str, event: dict[str, Any]) -> bool:
        try:
            if not self.producer:
                raise RuntimeError("Producer not started")
            await self.producer.send_and_wait(topic, event)
            return True
        except Exception as e:
            print(f"Failed to send event: {e}")
            return False
