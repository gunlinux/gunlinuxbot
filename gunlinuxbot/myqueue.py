from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, cast
import json

from redis import asyncio as aioredis

from gunlinuxbot.models.myqueue import QueueMessage, QueueMessageStatus
from gunlinuxbot.schemas.myqueue import QueueMessageSchema

if TYPE_CHECKING:
    from redis.asyncio.client import Redis
from redis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)

from .utils import logger_setup

logger = logger_setup('gunlinuxbot.myqueue')


class Connection(ABC):
    @abstractmethod
    async def push(self, name: str, data: str) -> None: ...

    @abstractmethod
    async def pop(self, name: str) -> str: ...

    @abstractmethod
    async def llen(self, name: str) -> int: ...

    @abstractmethod
    async def walk(self, name: str) -> list[Any]: ...

    @abstractmethod
    async def clean(self, name: str) -> None: ...


class RedisConnection(Connection):
    def __init__(self, url: str) -> None:
        self.url = url
        self._redis: Redis = aioredis.from_url(self.url)

    async def __adel__(self) -> None:
        if self._redis:
            await self._redis.close()

    async def push(self, name: str, data: str) -> None:
        if self._redis is None:
            logger.critical('cant push no redis conn')
            return
        try:
            await self._redis.rpush(name, data)
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant push no redis conn, %s', e)

    async def pop(self, name: str) -> str:
        if self._redis is None:
            logger.critical('cant pop no redis conn')
            return ''
        try:
            temp = await self._redis.lpop(name)
            if temp and isinstance(temp, bytes):
                return temp.decode('utf-8')
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant pop from redis conn, %s', e)
            return ''
        return temp

    async def llen(self, name: str) -> int:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return 0
        try:
            return await self._redis.llen(name)
        except (ConnectionError, TimeoutError):
            logger.exception('Failed to get length from Redis')
            raise

    async def walk(self, name: str) -> list[Any]:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return []
        try:
            return await self._redis.lrange(name, 0, -1)
        except (ConnectionError, TimeoutError):
            logger.exception('Failed to walk Redis')
            raise

    async def clean(self, name: str) -> None:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
        try:
            await self._redis.delete(name)
        except (ConnectionError, TimeoutError):
            logger.exception('cant llen from redis conn')


class Queue:
    def __init__(self, name: str, connection: Connection, max_retry: int = 5) -> None:
        self.name: str = name
        self.last_id: str | None = None
        self.connection: Connection = connection
        self.max_retry: int = max_retry

    async def push(self, data: QueueMessage) -> None:
        if data.status == QueueMessageStatus.PROCESSING:
            data.retry += 1
            data.status = QueueMessageStatus.WAITING

        if data.retry > self.max_retry:
            logger.critical('message retried more than %s %s', self.max_retry, data)
            return

        queue_message_dict = data.to_serializable_dict()
        await self.connection.push(self.name, json.dumps(queue_message_dict))

    async def pop(self) -> QueueMessage | None:
        temp_data: str = await self.connection.pop(self.name)
        if not temp_data:
            return None
        message: QueueMessage = cast(
            'QueueMessage', QueueMessageSchema().load(json.loads(temp_data))
        )
        message.status = QueueMessageStatus.PROCESSING
        return message

    async def llen(self) -> int | None:
        return await self.connection.llen(self.name)

    async def walk(self) -> list[Any]:
        return await self.connection.walk(self.name)

    async def clean(self) -> None:
        return await self.connection.clean(self.name)

    def __str__(self) -> str:
        return f'<Queue {self.name}>'
