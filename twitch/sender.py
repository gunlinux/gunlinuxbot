import asyncio
import os
import logging
import json
from datetime import datetime

from dotenv import load_dotenv
from myqueue import RedisConnection, Queue


logger = logging.getLogger(__name__)


class Sender:
    def __init__(self, queue: Queue):
        self.queue = queue

    async def send_message(self, message):
        event = {
            "event": "mssg",
            "timestamp": datetime.timestamp(datetime.now()),
            "data": {"message": message},
        }
        await self.queue.push(json.dumps(event))


async def main():
    load_dotenv()
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="twitch_out")
    queue = Queue(connection=redis_connection)
    sender = Sender(queue=queue)
    await sender.send_message("okface привет как ты")


if __name__ == "__main__":
    asyncio.run(main())
