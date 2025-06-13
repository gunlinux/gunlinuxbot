import asyncio
import logging
import os
import json
from collections.abc import Callable, Coroutine, Mapping
from typing import Any, cast, TYPE_CHECKING

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from requeue.schemas import QueueMessageSchema
from twitch.schemas import TwitchMessageSchema
from gunlinuxbot.twitch.twitchbot import TwitchBotGetter
from gunlinuxbot.utils import logger_setup

if TYPE_CHECKING:
    from requeue.models import QueueMessage
    from twitch.models import TwitchMessage

from twitchio.message import Message


logger = logger_setup('twitch_sender')
twitchio_logger = logging.getLogger('twitchio')
twitchio_logger.setLevel(logging.INFO)


async def init_process(
    queue: Queue,
) -> Callable[['Message'], Coroutine[Any, Any, None]]:
    process_queue: Queue = queue

    async def process_mssg(message: Message) -> None:
        twitch_message: TwitchMessage = cast(
            'TwitchMessage', TwitchMessageSchema().load(cast('Mapping', message))
        )
        payload: QueueMessage = cast(
            'QueueMessage',
            QueueMessageSchema().load(
                {
                    'event': 'twitch_message',
                    'data': json.dumps(twitch_message.to_serializable_dict()),
                },
            ),
        )
        await process_queue.push(payload)

    return process_mssg


async def main() -> None:
    access_token: str = os.environ.get('ACCESS_TOKEN', 'set_Dame_token')
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='twitch_mssgs', connection=redis_connection)

        event_loop = asyncio.get_running_loop()
        handler = await init_process(queue)
        bot = TwitchBotGetter(
            access_token=access_token, loop=event_loop, handler=handler
        )
        await bot.start()


if __name__ == '__main__':
    asyncio.run(main())
