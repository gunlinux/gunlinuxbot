import asyncio
import datetime
import json
import os
from typing import cast, TYPE_CHECKING

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError
from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.schemas.myqueue import QueueMessageSchema
from gunlinuxbot.utils import logger_setup

if TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage

logger = logger_setup('twitch_sender')


async def process(event: str) -> None:
    data_dict = json.loads(event)
    data: QueueMessage = cast('QueueMessage', QueueMessageSchema().load(data_dict))
    logger.debug('%s process %s %s', __name__, data.event, data.timestamp)

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
        new_event = await queue.pop()
        if new_event:
            try:
                await process(new_event)
            except ClientConnectorError:
                await queue.push(new_event)
        await asyncio.sleep(2)


async def main() -> None:
    load_dotenv()
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='bs_donats', connection=redis_connection)
    await asyncio.gather(sender(queue=queue))


if __name__ == '__main__':
    asyncio.run(main())
