import asyncio
import json
import os
from collections.abc import Callable, Coroutine
from dataclasses import asdict
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

from gunlinuxbot.donats import donats
from gunlinuxbot.handlers import Event
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup

logger = logger_setup("donats_getter")


async def init_process(
    queue: Queue,
) -> Callable[[Event], Coroutine[Any, Any, None]]:
    work_queue: Queue = queue

    async def process_mssg(message: Event) -> None:
        if not message:
            return
        payload = {
            "event": "da_message",
            "timestamp": datetime.timestamp(datetime.now()),
            "data": asdict(message),
        }
        logger.debug("new process_mssg da_events %s", payload)
        await work_queue.push(json.dumps(payload))
    return process_mssg


async def main() -> None:
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
