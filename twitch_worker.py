import asyncio
import os
import logging
import json
import random

from dotenv import load_dotenv

from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.sender import Sender
from gunlinuxbot.handlers import TwitchEventHandler, HandlerEvent, Command


logger = logging.getLogger(__name__)


async def process(handler: HandlerEvent, data):
    data = json.loads(data)
    payload_data = data.get("data", {})
    mssg = payload_data.get("content", "")
    user = payload_data.get("author", {}).get("name")
    if not mssg or not user:
        return
    event = HandlerEvent(mssg=mssg, user=user)
    await handler.handle_event(event)
    logger.critical("something happened %s", event)
    await asyncio.sleep(1)


async def auf(event: HandlerEvent):
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
    redis_connection = RedisConnection(redis_url, name="twitch_mssgs")
    redis_sender_connection = RedisConnection(redis_url, name="twitch_out")

    queue = Queue(connection=redis_connection)
    sender_queue = Queue(connection=redis_sender_connection)
    sender = Sender(queue=sender_queue)
    twitch_handler = TwitchEventHandler(sender=sender, admin="gunlinux")

    Command("ауф", twitch_handler, real_runner=auf)
    Command("gunlinauf", twitch_handler, real_runner=auf)
    Command("awoo", twitch_handler, real_runner=auf)
    Command("auf", twitch_handler, real_runner=auf)

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=twitch_handler, data=new_event)
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
