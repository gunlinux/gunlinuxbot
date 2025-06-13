import asyncio
import json
import os
import signal
from typing import cast, TYPE_CHECKING

from gunlinuxbot.models.event import Event
from donats.handlers import DonatEventHandler
from requeue.models import QueueMessage
from donats.schemas import AlertEventSchema
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

if TYPE_CHECKING:
    from donats.models import AlertEvent

logger = logger_setup('donats_worker')
logger.info('Donats worker service started')


async def process(handler: DonatEventHandler, message: QueueMessage) -> None:
    logger.debug('Processing new event from queue')
    data_json = json.loads(message.data)
    logger.debug('Received message data: %s', data_json)
    event: AlertEvent = cast('AlertEvent', AlertEventSchema().load(data_json))
    logger.debug('Processed event: %s', event)
    await handler.handle_event(event)
    await asyncio.sleep(1)


async def test_event(event: Event) -> str:
    logger.debug('test_event got event %s', event)
    return '#shitcode'


async def main() -> None:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue = Queue(name='da_events', connection=redis_connection)
        sender = Sender(queue_name='twitch_out', connection=redis_connection)
        donat_handler: DonatEventHandler = DonatEventHandler(
            sender=sender,
            admin='gunlinux',
        )

        # Setup graceful shutdown
        stop_event = asyncio.Event()

        def signal_handler(sig: int, _frame: object) -> None:
            logger.info('Received shutdown signal: %s', signal.strsignal(sig))
            logger.info('Stopping gracefully...')
            stop_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            while not stop_event.is_set():
                logger.debug('Checking queue for new events')
                new_event: QueueMessage | None = await queue.pop()
                if new_event is not None:
                    logger.debug('Found new event to process')
                    await process(handler=donat_handler, message=new_event)
                await asyncio.sleep(1)
        finally:
            logger.info('Donats worker service is shutting down')


if __name__ == '__main__':
    asyncio.run(main())
