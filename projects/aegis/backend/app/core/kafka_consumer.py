from aiokafka import AIOKafkaConsumer
from typing import Callable, Awaitable
import json

class KafkaConsumer:
    def __init__(self, bootstrap_servers: list[str], group_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode())
        )

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    async def subscribe(self, topics: list[str]):
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        await self.consumer.start()
        await self.consumer.subscribe(topics)

    async def consume(self, handler: Callable[[dict], Awaitable[None]]):
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        async for message in self.consumer:
            await handler(message.value)
