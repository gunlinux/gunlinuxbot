import asyncio
import os
from collections.abc import Callable, Coroutine
import typing
import json

from donats.donats import DonatApi
from gunlinuxbot.models import Event
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from requeue.schemas import QueueMessageSchema
from gunlinuxbot.utils import logger_setup

if typing.TYPE_CHECKING:
    from requeue.models import QueueMessage
    from donats.models import AlertEvent

logger = logger_setup('donats_getter')
logger.info('Donats getter service started')


async def init_process(
    queue: Queue,
    redis_connection: RedisConnection,
) -> Callable[[Event], Coroutine[typing.Any, typing.Any, None]]:
    work_queue: Queue = queue
    events_queue = Queue(name='local_events', connection=redis_connection)
    beer_queue = Queue(name='bs_donats', connection=redis_connection)

    async def process_mssg(message: Event) -> None:
        logger.debug('Received message for processing')
        logger.debug('Message content: %s', message)
        message = typing.cast('AlertEvent', message)
        message_dict = message.serialize()
        message_id = message_dict.get('id', None)
        logger.debug('Processing message ID: %s', message_id)
        if queue.last_id and queue.last_id == message_id:
            logger.critical('Duplicate message detected: %s', message_id)
            await asyncio.sleep(0.1)
            return
        queue.last_id = message_id
        payload = {
            'event': 'da_message',
            'data': json.dumps(message_dict),
        }
        logger.debug('Preparing message for queue: %s', payload)
        new_message: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload)
        )
        await events_queue.push(new_message)
        await work_queue.push(new_message)
        await beer_queue.push(new_message)
        logger.critical('saving new_message to a works queues')

    return process_mssg


async def main() -> None:
    access_token = os.environ.get('DA_ACCESS_TOKEN', 'set_Dame_token')
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    logger.info('Initializing donats getter service')
    logger.info('Redis URL: %s', redis_url)
    async with RedisConnection(redis_url) as redis_connection:
        queue = Queue(name='da_events', connection=redis_connection)

        handler = await init_process(
            queue, typing.cast('RedisConnection', redis_connection)
        )
        bot = DonatApi(token=access_token, handler=handler)
        while True:
            try:
                logger.info('restart donats bot')
                await bot.run()
            except Exception as e:  # noqa: BLE001, PERF203
                logger.warning('Connection error we are reconnecting', exc_info=e)


if __name__ == '__main__':
    asyncio.run(main())
