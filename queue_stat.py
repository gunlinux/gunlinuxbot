import asyncio
import os

from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def get_queue_stat(queue: str) -> dict:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url, name=queue)
    queue = Queue(connection=redis_connection)
    logger.info('%s %s', queue, await queue.llen())
    for rec in await queue.walk():
        logger.info(rec)


async def get_queues_stat() -> None:
    load_dotenv()
    queues = ['da_evens', 'twitch_mssgs', 'twitch_out']
    for queue in queues:
        await get_queue_stat(queue)


if __name__ == '__main__':
    asyncio.run(get_queues_stat())
