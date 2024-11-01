import asyncio
import os
import logging
import json
from datetime import datetime

from dotenv import load_dotenv
import gunlinuxbot.donats.donats as donats
from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.handlers import HandlerEvent
from dataclasses import asdict


logger = logging.getLogger(__name__)


async def init_process(queue):
    queue = queue

    async def process_mssg(message: HandlerEvent):
        if not message:
            return
        payload = {
            "event": "da_message",
            "timestamp": datetime.timestamp(datetime.now()),
            "data": asdict(message),
        }
        print(f' new process_mssg da_events {payload}')
        await queue.push(json.dumps(payload))
    return process_mssg


async def main():
    load_dotenv()
    access_token = os.environ.get("DA_ACCESS_TOKEN", "set_Dame_token")
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="da_events")
    queue = Queue(connection=redis_connection)
    handler = await init_process(queue)
    bot = donats.DonatApi(token=access_token, handler=handler)
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
