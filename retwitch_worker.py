import asyncio
import os

from gunlinuxbot.models import Event
from retwitch.handlers import RetwitchEventHandler
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from sender.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('donats_worker')
logger.info('Donats worker service started')


async def test_event(event: Event) -> str:
    logger.debug('test_event got event %s', event)
    return '#shitcode'


async def main() -> None:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='retwitch_mssgs', connection=redis_connection)
        sender = Sender(queue_name='twitch_out', connection=redis_connection)
        retwitch_handler: RetwitchEventHandler = RetwitchEventHandler(
            sender=sender,
            admin='gunlinux',
        )
        await queue.consumer(retwitch_handler.on_message)


if __name__ == '__main__':
    asyncio.run(main())
