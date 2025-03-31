import asyncio
import json
import os
import signal
from typing import Optional

from dotenv import load_dotenv

from gunlinuxbot.handlers import DonatEventHandler, Event, EventHandler
from gunlinuxbot.schemas.donats import AlertEventSchema
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('donats_worker')


async def process(handler: EventHandler, data: str) -> None:
    if not data or data == 'None':
        logger.debug('Received empty data, skipping')
        return
    json_data: dict = json.loads(data)
    payload_data = json_data.get('data', {})
    logger.critical('data %s', payload_data)
    event = AlertEventSchema().load(payload_data)
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
    
    def signal_handler(sig: int, frame: Optional[object]) -> None:
        logger.info('Received shutdown signal, stopping gracefully...')
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        while not stop_event.is_set():
            try:
                new_event = await queue.pop()
                if new_event:
                    await process(handler=donat_handler, data=new_event)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error('Error in main loop: %s', str(e))
                await asyncio.sleep(1)
    finally:
        logger.info('Shutting down...')


if __name__ == '__main__':
    asyncio.run(main())
