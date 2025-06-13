import asyncio
import os
import logging
import typing

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from gunlinuxbot.twitch.twitchbot import TwitchBotSender
from gunlinuxbot.utils import logger_setup

from requeue.models import QueueMessage

logger = logger_setup('twitch_sender')
twitchio_logger = logging.getLogger('twitchio')
twitchio_logger.setLevel(logging.INFO)


async def init_process(bot: TwitchBotSender) -> typing.Any:
    async def process(message: QueueMessage) -> None:
        logger.debug('%s process %s', __name__, message.event)
        if message.data:
            await bot.send_message(message.data)
    return process


async def sender(bot: TwitchBotSender, queue: Queue) -> None:
    logger.debug('sender start')
    process = await init_process(bot)
    await queue.consumer(process)


async def main() -> None:
    access_token: str = os.environ.get('ACCESS_TOKEN', 'set_Dame_token')
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='twitch_out', connection=redis_connection)

        event_loop = asyncio.get_running_loop()
        bot = TwitchBotSender(access_token=access_token, loop=event_loop)
        _ = await asyncio.gather(sender(bot, queue), bot.start())


if __name__ == '__main__':
    asyncio.run(main())
