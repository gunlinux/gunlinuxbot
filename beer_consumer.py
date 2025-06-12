import asyncio
import datetime
import json
import os

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from gunlinuxbot.utils import logger_setup

from requeue.models import QueueMessage

logger = logger_setup('twitch_sender')


async def process(data: QueueMessage) -> None:
    logger.debug('%s process %s', __name__, data.event)

    url = 'http://127.0.0.1:6016/donate'
    stat_data = json.loads(data.data)
    payload = {
        'date': datetime.datetime.now().isoformat(),
        'value': stat_data.get('value', 0),
        'name': stat_data.get('name'),
    }
    headers = {
        'Content-Type': 'application/json',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()


async def sender(queue: Queue) -> None:
    logger.debug('bs sender start')
    while True:
        new_event: QueueMessage | None = await queue.pop()
        if new_event is not None:
            try:
                await process(new_event)
            except ClientConnectorError:
                await queue.push(new_event)
        await asyncio.sleep(2)


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='bs_donats', connection=redis_connection)
        await asyncio.gather(sender(queue=queue))


if __name__ == '__main__':
    asyncio.run(main())
