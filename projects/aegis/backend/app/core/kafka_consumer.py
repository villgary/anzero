from aiokafka import AIOKafkaConsumer
from typing import Callable, Awaitable, Optional
import logging
import json
import asyncio

logger = logging.getLogger(__name__)

class KafkaConsumer:
    def __init__(self, bootstrap_servers: list[str], group_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._stop_event: Optional[asyncio.Event] = None

    async def start(self) -> None:
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode())
        )
        await self.consumer.start()
        self._stop_event = asyncio.Event()

    async def stop(self) -> None:
        if self._stop_event:
            self._stop_event.set()
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def subscribe(self, topics: list[str]) -> None:
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        await self.consumer.subscribe(topics)

    async def consume(self, handler: Callable[[dict], Awaitable[None]]) -> None:
        if not self.consumer:
            raise RuntimeError("Consumer not started")
        if not self._stop_event:
            raise RuntimeError("Consumer not started")
        try:
            async for message in self.consumer:
                if self._stop_event.is_set():
                    break
                await handler(message.value)
        except asyncio.CancelledError:
            logger.info("Consumer cancelled, shutting down...")
            raise
