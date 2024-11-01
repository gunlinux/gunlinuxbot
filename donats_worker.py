import asyncio
import os
import logging
import json
import random

from dotenv import load_dotenv

from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.sender import Sender
from gunlinuxbot.handlers import DonatEventHandler, HandlerEvent, Command


logger = logging.getLogger(__name__)


async def process(handler: HandlerEvent, data):
    data = json.loads(data)
    payload_data = data.get("data", {})
    event = HandlerEvent(**payload_data)
    print(f'process new event {event}')
    await handler.handle_event(event)
    logger.critical("something happened %s", event)
    await asyncio.sleep(1)


async def test_event(event: HandlerEvent):
    print(f'test_event process {event}')
    return 'okface'
    symbols = ["AWOO", "AUF", "gunlinAuf"]
    symbols_len = random.randint(6, 12)
    out = []
    for _ in range(symbols_len):
        out.append(random.choice(symbols))

    auf_str = " ".join(out)
    return f"@{event.user} Воистину {auf_str}"


async def main():
    load_dotenv()
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="da_events")
    redis_sender_connection = RedisConnection(redis_url, name="twitch_out")

    queue = Queue(connection=redis_connection)
    sender_queue = Queue(connection=redis_sender_connection)
    sender = Sender(queue=sender_queue)
    donat_handler = DonatEventHandler(sender=sender, admin="gunlinux")
    Command("#shitcode", donat_handler, real_runner=test_event)

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=donat_handler, data=new_event)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
