import asyncio
import os

from dotenv import load_dotenv

from .myqueue import Connection, Queue, RedisConnection
from .utils import logger_setup
from gunlinuxbot.schemas.myqueue import QueueMessageSchema

logger = logger_setup('gunlinuxbot.sender')


class Sender:
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


async def main() -> None:
    load_dotenv()
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='twitch_out', connection=redis_connection)
    sender = Sender(queue=queue)
    await sender.send_message('okface привет как ты')


if __name__ == '__main__':
    asyncio.run(main())
