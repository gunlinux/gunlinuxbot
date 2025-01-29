import asyncio
import json
import os
import random
from collections.abc import Awaitable, Callable
from typing import Any

from dotenv import load_dotenv

from gunlinuxbot.handlers import Command, Event, EventHandler, TwitchEventHandler
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitch_worker')


async def process(handler: EventHandler, data: str) -> None:
    process_data: dict = json.loads(data)
    payload_data = process_data.get('data', {})
    mssg = payload_data.get('content', '')
    user = payload_data.get('author', {}).get('name')
    if not mssg or not user:
        return
    event: Event = Event(mssg=mssg, user=user)
    await handler.handle_event(event)
    logger.critical('something happened %s', event)
    await asyncio.sleep(1)
    return


async def auf(event: Event, post: Awaitable[Any] | Callable | None = None) -> str:
    logger.critical('auf')
    symbols = ['AWOO', 'AUF', 'gunlinAuf']
    symbols_len = random.randint(6, 12) #  noqa: S311
    out = [random.choice(symbols) for _ in range(symbols_len)] # noqa: S311

    auf_str = ' '.join(out)
    logger.critical('%s %s', auf_str, event)
    temp =  f'@{event.user} Воистину {auf_str}'
    logger.critical('auf end %s', temp)

    if post:
        return await post(temp)
    return temp


async def main() -> Awaitable[None]:
    load_dotenv()
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url, name='twitch_mssgs')
    redis_sender_connection = RedisConnection(redis_url, name='twitch_out')

    queue = Queue(connection=redis_connection)
    sender_queue = Queue(connection=redis_sender_connection)
    sender = Sender(queue=sender_queue)
    twitch_handler = TwitchEventHandler(sender=sender, admin='gunlinux')

    Command('ауф', twitch_handler, real_runner=auf)
    Command('gunlinAuf', twitch_handler, real_runner=auf)
    Command('awoo', twitch_handler, real_runner=auf)
    Command('auf', twitch_handler, real_runner=auf)
    await asyncio.sleep(1)

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=twitch_handler, data=new_event)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
