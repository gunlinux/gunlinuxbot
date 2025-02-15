import asyncio
import json
import os
from datetime import datetime

from dotenv import load_dotenv

from .myqueue import Queue, RedisConnection
from .utils import logger_setup

logger = logger_setup('gunlinuxbot.sender')


class Sender:
    def __init__(self, queue: Queue) -> None:
        self.queue = queue

    async def send_message(self, message: str) -> None:
        event = {
            "event": "mssg",
            "timestamp": datetime.now().timestamp(),
            "data": {"message": message},
        }
        await self.queue.push(json.dumps(event))


async def main() -> None:
    load_dotenv()
    redis_url = os.getenv("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="twitch_out")
    queue = Queue(connection=redis_connection)
    sender = Sender(queue=queue)
    await sender.send_message("okface привет как ты")


if __name__ == "__main__":
    asyncio.run(main())
