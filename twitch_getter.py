import asyncio
import logging
import os
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.schemas.myqueue import QueueMessageSchema
from gunlinuxbot.schemas.twitch import TwitchMessageSchema
from gunlinuxbot.twitch.twitchbot import TwitchBotGetter
from gunlinuxbot.utils import dump_json, logger_setup

if TYPE_CHECKING:
    from twitchio.message import Message


logger = logger_setup('twitch_sender')
twitchio_logger = logging.getLogger('twitchio')
twitchio_logger.setLevel(logging.INFO)


async def init_process(
    queue: Queue,
) -> Callable[['Message'], Coroutine[Any, Any, None]]:
    process_queue: Queue = queue

    async def process_mssg(message: 'Message') -> None:
        if not message:
            return
        twitch_message = TwitchMessageSchema().load(data=message)
        payload = QueueMessageSchema().load(
            {
                'event': 'twitch_message',
                'data': dump_json(twitch_message),
            },
        )
        await process_queue.push(payload)

    return process_mssg


async def main() -> None:
    load_dotenv()
    access_token: str = os.environ.get('ACCESS_TOKEN', 'set_Dame_token')
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='twitch_mssgs', connection=redis_connection)

    event_loop = asyncio.get_running_loop()
    handler = await init_process(queue)
    bot = TwitchBotGetter(access_token=access_token, loop=event_loop, handler=handler)
    await bot.start()


if __name__ == '__main__':
    asyncio.run(main())
