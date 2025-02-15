import asyncio
import json
import os

from dotenv import load_dotenv

from gunlinuxbot.handlers import DonatEventHandler, Event, EventHandler
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('donats_worker')


async def process(handler: EventHandler, data: str) -> None:
    if not data or data == 'None':
        return
    json_data: dict = json.loads(data)
    payload_data = json_data.get("data", {})
    logger.critical('data %s', payload_data)
    event: Event = Event(**payload_data)
    logger.debug('process new event %s', event)
    await handler.handle_event(event)
    await asyncio.sleep(1)


async def test_event(event: Event) -> str:
    logger.debug('test_event got event %s', event)
    return '#shitcode'


async def main() -> None:
    load_dotenv()
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url)

    queue = Queue(name="da_events", connection=redis_connection)
    sender_queue = Queue(name="twitch_out", connection=redis_connection)
    sender = Sender(queue=sender_queue)
    donat_handler: EventHandler = DonatEventHandler(sender=sender, admin="gunlinux")

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=donat_handler, data=new_event)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
