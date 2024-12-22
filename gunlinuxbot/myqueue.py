from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from redis import asyncio as aioredis

if TYPE_CHECKING:
    from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError, TimeoutError

from .utils import logger_setup

logger = logger_setup('gunlinuxbot.myqueue')


class Connection(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def push(self, data: str) -> None:
        pass

    @abstractmethod
    async def pop(self) -> str | None:
        pass

    @abstractmethod
    async def llen(self) -> int | None:
        pass

    @abstractmethod
    async def walk(self) -> list[Any]:
        pass

    @abstractmethod
    async def clean(self) -> None:
        pass


class RedisConnection(Connection):
    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self._name: str = name
        self.redis: Redis = aioredis.from_url(self.url)

    async def __adel__(self) -> None:
        if self.redis:
            await self.redis.close()

    async def push(self, data: str) -> None:
        if self.redis is None:
            logger.critical('cant push no redis conn')
            return
        try:
            await self.redis.rpush(self.name, data)
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant push no redis conn, %s', e)

    @property
    def name(self) -> str:
        return self._name

    async def pop(self) -> str | None:
        if self.redis is None:
            logger.critical('cant pop no redis conn')
            return None
        try:
            return await self.redis.lpop(self.name) # type: ignore[misc]
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant pop from redis conn, %s', e)
        return None

    async def llen(self) -> int | None:
        if self.redis is None:
            logger.critical('cant llen no redis conn')
            return None
        try:
            return await self.redis.llen(self.name) # type: ignore[misc]
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)
        return None

    async def walk(self) -> list[Any]:
        if self.redis is None:
            logger.critical('cant llen no redis conn')
            return []
        try:
            return await self.redis.lrange(self.name, 0, -1) # type: ignore[misc]
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)
        return []

    async def clean(self) -> None:
        if self.redis is None:
            logger.critical('cant llen no redis conn')
            return None
        try:
            return await self.redis.delete(self.name)
        except (ConnectionError, TimeoutError) as e:
            logger.critical('cant llen from redis conn, %s', e)




class Queue:
    def __init__(self, connection: Connection) -> None:
        self.connection: Connection = connection

    async def push(self, data: str) -> None:
        await self.connection.push(data)

    async def pop(self) -> str | None:
        return await self.connection.pop()

    async def llen(self) -> int | None:
        return await self.connection.llen()

    async def walk(self) -> list[Any]:
        return await self.connection.walk()

    async def clean(self) -> None:
        return await self.connection.clean()

    def __str__(self) -> str:
        return f'<Queue {self.connection.name}>'
