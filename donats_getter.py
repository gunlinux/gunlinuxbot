import asyncio
import json
import os
from collections.abc import Callable, Coroutine
from dataclasses import asdict
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from socketio.exceptions import SocketIOError

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
            logger.critical('process_mssg no message')
            return
        message_dict = asdict(message)
        message_id = message_dict.get('id', None)
        if queue.last_id and queue.last_id == message_id:
            # doesnt repeat itself
            logger.critical('dont repeat itself')
            await asyncio.sleep(0.1)
            return
        queue.last_id = message_id
        message_dict.get('id', None)
        payload = {
            "event": "da_message",
            "timestamp": datetime.timestamp(datetime.now()),
            "data": message_dict,
        }
        logger.debug("new process_mssg da_events %s", payload)
        await work_queue.push(json.dumps(payload))
    return process_mssg


async def main() -> None:
    load_dotenv()
    access_token = os.environ.get("DA_ACCESS_TOKEN", "set_Dame_token")
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url)
    queue = Queue(name="da_events", connection=redis_connection)

    while True:
        handler = await init_process(queue)
        bot = donats.DonatApi(token=access_token, handler=handler)
        try:
            await bot.run()
        except SocketIOError as e:
            logger.critical('some exception caught %s', e.__class__)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
