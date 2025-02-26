from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from redis import asyncio as aioredis

if TYPE_CHECKING:
    from redis.asyncio.client import Redis
from redis.exceptions import (
        ConnectionError as RedisConnectionError,
        TimeoutError as RedisTimeoutError,
)
from gunlinuxbot.models.myqueue import QueueMessage

from .utils import logger_setup, dump_json

logger = logger_setup('gunlinuxbot.myqueue')


class Connection(ABC):

    @abstractmethod
    async def push(self, name: str, data: str) -> None:
        ...

    @abstractmethod
    async def pop(self, name: str) -> str | None:
        ...

    @abstractmethod
    async def llen(self, name: str) -> int | None:
        ...

    @abstractmethod
    async def walk(self, name: str) -> list[Any]:
        ...

    @abstractmethod
    async def clean(self, name: str) -> None:
        ...


class RedisConnection(Connection):
    def __init__(self, url: str) -> None:
        self.url = url
        self._redis: Redis = aioredis.from_url(self.url)

    async def __adel__(self) -> None:
        if self._redis:
            await self._redis.close()

    async def push(self, name: str, data: QueueMessage) -> None:
        if self._redis is None:
            logger.critical('cant push no redis conn')
            return
        try:
            await self._redis.rpush(name, dump_json(data))
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant push no redis conn, %s', e)

    async def pop(self, name: str) -> str | None:
        if self._redis is None:
            logger.critical('cant pop no redis conn')
            return None
        try:
            return await self._redis.lpop(name)
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant pop from redis conn, %s', e)
        return None

    async def llen(self, name: str) -> int | None:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return None
        try:
            return await self._redis.llen(name)
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)
        return None

    async def walk(self, name: str) -> list[Any]:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return []
        try:
            return await self._redis.lrange(name, 0, -1)
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)
        return []

    async def clean(self, name: str) -> None:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return None
        try:
            return await self._redis.delete(name)
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)
        return None


class Queue:
    def __init__(self, name: str, connection: Connection) -> None:
        self.name: str = name
        self.last_id: str | None = None
        self.connection: Connection = connection

    async def push(self, data: str) -> None:
        await self.connection.push(self.name, data)

    async def pop(self) -> str | None:
        return await self.connection.pop(self.name)

    async def llen(self) -> int | None:
        return await self.connection.llen(self.name)

    async def walk(self) -> list[Any]:
        return await self.connection.walk(self.name)

    async def clean(self) -> None:
        return await self.connection.clean(self.name)

    def __str__(self) -> str:
        return f'<Queue {self.name}>'
