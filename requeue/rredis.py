from abc import ABC, abstractmethod
from types import TracebackType
import typing
import asyncio
from typing_extensions import override
import logging

from coredis import Redis


from coredis.exceptions import (
    ConnectionError as RedisConnectionError,
    TimeoutError as RedisTimeoutError,
)


logger = logging.getLogger('rredis')


class Connection(ABC):
    @abstractmethod
    async def push(self, name: str, data: str) -> None: ...

    @abstractmethod
    async def pop(self, name: str) -> str: ...

    @abstractmethod
    async def llen(self, name: str) -> int: ...

    @abstractmethod
    async def walk(self, name: str) -> list[str]: ...

    @abstractmethod
    async def clean(self, name: str) -> None: ...

    @abstractmethod
    async def _connect(self) -> None: ...

    @abstractmethod
    async def _close(self) -> None: ...

    async def __aenter__(self) -> 'Connection':
        await self._connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._close()


class RedisConnection(Connection):
    def __init__(self, url: str) -> None:
        self.url: str = url
        self._redis: Redis[str] | None = None

    @override
    async def _connect(self):
        if self._redis is None:
            self._redis = await Redis.from_url(
                self.url,
                decode_responses=True,
                protocol_version=2,
            )

    @override
    async def _close(self):
        self._redis = None

    @override
    async def push(self, name: str, data: str) -> None:
        if self._redis is None:
            logger.critical('cant push no redis conn')
            return
        try:
            _ = await self._redis.rpush(name, [data])
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant push no redis conn, %s', e)

    @override
    async def pop(self, name: str) -> str:
        if self._redis is None:
            logger.critical('cant pop no redis conn')
            return ''
        try:
            temp: str | None = await self._redis.lpop(name)
            if temp and isinstance(temp, bytes):
                return temp.decode('utf-8')
        except (RedisConnectionError, RedisTimeoutError) as e:
            logger.critical('cant pop from redis conn, %s', e)
            return ''
        return typing.cast('str', temp)

    @override
    async def llen(self, name: str) -> int:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return 0
        try:
            return await self._redis.llen(name)
        except (ConnectionError, TimeoutError):
            logger.exception('Failed to get length from Redis')
            raise

    @override
    async def walk(self, name: str) -> list[str]:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return []
        try:
            return await self._redis.lrange(name, 0, -1)
        except (ConnectionError, TimeoutError):
            logger.exception('Failed to walk Redis')
            raise

    @override
    async def clean(self, name: str) -> None:
        if self._redis is None:
            logger.critical('cant llen no redis conn')
            return
        try:
            _ = await self._redis.delete([name])
        except (ConnectionError, TimeoutError):
            logger.exception('cant llen from redis conn')


async def main() -> None:
    async with RedisConnection('redis://localhost/1') as conn:
        print(conn)
        await conn.push('q', 'loki')
        print(await conn.pop('q'))


if __name__ == '__main__':
    asyncio.run(main())
