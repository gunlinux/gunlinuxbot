import asyncio
import json
import os
import signal
from typing import cast, TYPE_CHECKING

from dotenv import load_dotenv

from gunlinuxbot.handlers import DonatEventHandler, Event, EventHandler
from gunlinuxbot.models.myqueue import QueueMessage
from gunlinuxbot.schemas.donats import AlertEventSchema
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

if TYPE_CHECKING:
    from gunlinuxbot.models.donats import AlertEvent

logger = logger_setup('donats_worker')


async def process(handler: EventHandler, message: QueueMessage) -> None:
    data_json = json.loads(message.data)
    event: AlertEvent = cast('AlertEvent', AlertEventSchema().load(data_json))
    logger.debug('process new event %s', event)
    await handler.handle_event(event)
    await asyncio.sleep(1)


async def test_event(event: Event) -> str:
    logger.debug('test_event got event %s', event)
    return '#shitcode'


async def main() -> None:
    load_dotenv()
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url)

    queue = Queue(name='da_events', connection=redis_connection)
    sender = Sender(queue_name='twitch_out', connection=redis_connection)
    donat_handler: EventHandler = DonatEventHandler(
        sender=sender,
        admin='gunlinux',
    )

    # Setup graceful shutdown
    stop_event = asyncio.Event()

    def signal_handler(sig: int, frame: object | None) -> None:
        logger.info(
            'Received shutdown signal, stopping gracefully... %s %s', sig, frame
        )
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while not stop_event.is_set():
            new_event: QueueMessage | None = await queue.pop()
            if new_event is not None:
                await process(handler=donat_handler, message=new_event)
            await asyncio.sleep(1)
    finally:
        logger.info('Shutting down...')


if __name__ == '__main__':
    asyncio.run(main())
