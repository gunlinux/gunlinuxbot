import asyncio
import os

from dotenv import load_dotenv

from abc import ABC, abstractmethod

from .myqueue import Connection, Queue, RedisConnection
from .utils import logger_setup
from gunlinuxbot.schemas.myqueue import QueueMessageSchema

logger = logger_setup('gunlinuxbot.sender')


class SenderAbc(ABC):
    @abstractmethod
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None: ...

    @abstractmethod
    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None: ...


class Sender(SenderAbc):
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None:
        self.connection = connection
        self.queue = Queue(name=queue_name, connection=connection)
        self.source = source

    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None:
        payload = {
            'event': 'mssg',
            'data': message,
            'source': source or self.source,
        }
        message = QueueMessageSchema().load(payload)
        if not queue_name:
            await self.queue.push(message)
            return
        await Queue(name=queue_name, connection=self.connection).push(message)


class DummySender(SenderAbc):
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None:
        logger.debug('init dummy sender for q %s', queue_name)
        self.connection = connection
        self.queue_name = queue_name
        self.source = source

    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None:
        _ = source, queue_name
        logger.debug('send_message to %s "%s"', self.queue_name, message)


async def main() -> None:
    load_dotenv()
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='twitch_out', connection=redis_connection)
    sender = Sender(queue=queue)
    
    # Test message
    test_message = os.getenv('TEST_MESSAGE', 'okface привет как ты')
    await sender.send_message(test_message)


if __name__ == '__main__':
    asyncio.run(main())
