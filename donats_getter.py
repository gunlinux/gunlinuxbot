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
    processed = set()

    async def process_mssg(message: Event) -> None:
        nonlocal processed
        logger.debug('Received message for processing')
        logger.debug('Message content: %s', message)
        message = typing.cast('AlertEvent', message)
        message_dict = message.serialize()
        if message_dict.get('billing_system') == 'TWITCH':
            logger.debug('ignoring message from twitch: %s', message_dict)
            return
        message_id = message_dict.get('id', None)
        logger.debug('Processing message ID: %s', message_id)
        if message_id in processed:
            logger.critical('Duplicate message detected: %s', message_id)
            return
        processed.add(message_id)

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
    redis_url = os.environ.get('REDIS_URL', 'redis://gunlinux.ru/1')
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
                logger.info('start donats bot')
                await bot.run()
                logger.warning('bot.run() finished without an exception. Restarting...')
            except Exception as e:  # noqa: BLE001, PERF203
                logger.warning('Connection error we are reconnecting', exc_info=e)


if __name__ == '__main__':
    asyncio.run(main())
