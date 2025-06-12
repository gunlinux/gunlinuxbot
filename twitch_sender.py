import asyncio
import os
import logging

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from gunlinuxbot.twitch.twitchbot import TwitchBotSender
from gunlinuxbot.utils import logger_setup

from requeue.models import QueueMessage

logger = logger_setup('twitch_sender')
twitchio_logger = logging.getLogger('twitchio')
twitchio_logger.setLevel(logging.INFO)


def process(data: QueueMessage) -> str | None:
    logger.debug('%s process %s', __name__, data.event)
    return data.data


async def sender(bot: TwitchBotSender, queue: Queue) -> None:
    logger.debug('sender start')
    while True:
        new_event = await queue.pop()
        if new_event:
            mssg = process(new_event)
            if mssg:
                await bot.send_message(mssg)
        await asyncio.sleep(2)


async def main() -> None:
    access_token: str = os.environ.get('ACCESS_TOKEN', 'set_Dame_token')
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='twitch_out', connection=redis_connection)

        event_loop = asyncio.get_running_loop()
        bot = TwitchBotSender(access_token=access_token, loop=event_loop)
        await asyncio.gather(sender(bot, queue), bot.start())


if __name__ == '__main__':
    asyncio.run(main())
