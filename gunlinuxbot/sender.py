import asyncio
import os

from dotenv import load_dotenv

from .myqueue import Queue, RedisConnection
from .utils import logger_setup
from gunlinuxbot.schemas.queue import QueueMessageSchema

logger = logger_setup('gunlinuxbot.sender')


class Sender:
    def __init__(self, queue: Queue, source: str = '') -> None:
        self.queue = queue
        self.source = source

    async def send_message(self, message: str) -> None:
        message = QueueMessageSchema().load({
            "event": "mssg",
            "data": message,
            "source": self.source,
        })
        await self.queue.push(message)


async def main() -> None:
    load_dotenv()
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost/1")
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name="twitch_out", connection=redis_connection)
    sender = Sender(queue=queue)
    await sender.send_message("okface привет как ты")


if __name__ == "__main__":
    asyncio.run(main())
