from redis import asyncio as aioredis
from abc import ABC, abstractmethod
from typing import Any, Optional
from .utils import logger_setup
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError, TimeoutError


logger = logger_setup("gunlinuxbot.myqueue")


class Connection(ABC):
    @abstractmethod
    async def push(self, data):
        pass

    @abstractmethod
    async def pop(self) -> Any:
        pass


class RedisConnection(Connection):
    def __init__(self, url: str, name: str):
        self.url = url
        self.name: str = name
        self.redis: Redis = aioredis.from_url(self.url)

    async def push(self, data: str) -> None:
        if self.redis is None:
            logger.critical("cant push no redis conn")
            return
        try:
            await self.redis.rpush(self.name, data)  # type: ignore
        except (ConnectionError, TimeoutError) as e:
            logger.critical("cant push no redis conn, %s", e)

    async def pop(self) -> Optional[str]:
        if self.redis is None:
            logger.critical("cant pop no redis conn")
            return
        try:
            return await self.redis.lpop(self.name)  # type: ignore
        except (ConnectionError, TimeoutError) as e:
            logger.critical("cant pop from redis conn, %s", e)


class Queue:
    def __init__(self, connection: Connection):
        self.connection: Connection = connection

    async def push(self, data: str) -> None:
        await self.connection.push(data)

    async def pop(self) -> Optional[str]:
        return await self.connection.pop()
