import asyncio
import os
import json

from dotenv import load_dotenv

from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.sender import Sender
from gunlinuxbot.handlers import DonatEventHandler, Event, Command, EventHandler
from gunlinuxbot.utils import logger_setup


logger = logger_setup('donats_worker')


async def process(handler: EventHandler, data):
    data = json.loads(data)
    payload_data = data.get("data", {})
    event: Event = Event(**payload_data)
    logger.debug('process new event %s', event)
    await handler.handle_event(event)
    await asyncio.sleep(1)


async def test_event(event: Event):
    logger.debug('test_event got event %s', event)
    return '#shitcode'


async def main():
    load_dotenv()
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="da_events")
    redis_sender_connection = RedisConnection(redis_url, name="twitch_out")

    queue = Queue(connection=redis_connection)
    sender_queue = Queue(connection=redis_sender_connection)
    sender = Sender(queue=sender_queue)
    donat_handler: EventHandler = DonatEventHandler(sender=sender, admin="gunlinux")
    Command("#shitcode", donat_handler, real_runner=test_event)

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=donat_handler, data=new_event)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
