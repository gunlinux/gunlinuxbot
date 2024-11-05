from redis import asyncio as aioredis
import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from redis.asyncio.client import Redis


logger = logging.getLogger(__name__)


class Connection(ABC):
    @abstractmethod
    async def push(self, data):
        pass

    @abstractmethod
    async def pop(self) -> Any:
        pass


class RedisConnection(Connection):
    def __init__(self, url, name):
        self.url = url
        self.name: str = name
        self.redis: Redis = aioredis.from_url(self.url)

    async def push(self, data: str) -> None:
        await self.redis.rpush(self.name, data) #  type: ignore

    async def pop(self) -> Optional[str]:
        if self.redis is not None:
            return await self.redis.lpop(self.name) # type: ignore


class Queue:
    def __init__(self, connection: Connection):
        self.connection: Connection = connection

    async def push(self, data):
        await self.connection.push(data)

    async def pop(self):
        return await self.connection.pop()
