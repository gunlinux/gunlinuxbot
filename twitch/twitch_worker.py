import asyncio
import os
import logging
from dotenv import load_dotenv
from myqueue import RedisConnection, Queue


logger = logging.getLogger(__name__)


async def process(event):
    logger.critical("something happened %s", event)
    await asyncio.sleep(1)


async def main():
    load_dotenv()
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="twitch_mssgs")
    queue = Queue(connection=redis_connection)
    while True:
        new_event = await queue.pop()
        if new_event:
            await process(new_event)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
