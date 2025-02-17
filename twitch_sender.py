import asyncio
import json
import os

from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.twitch.twitchbot import TwitchBot
from gunlinuxbot.schemas.queue import QueueMessageSchema
from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitch_sender')


def process(event: str) -> str | None:
    data_dict = json.loads(event)
    data = QueueMessageSchema().load(data_dict)
    logger.debug('%s process %s %s', __name__ ,data.event, data.timestamp)
    return data.data


async def sender(bot: TwitchBot, queue: Queue) -> None:
    logger.debug("sender start")
    while True:
        new_event = await queue.pop()
        if new_event:
            mssg = process(new_event)
            if mssg:
                await bot.send_message(mssg)
        await asyncio.sleep(2)


async def main() -> None:
    load_dotenv()
    access_token: str = os.environ.get("ACCESS_TOKEN", "set_Dame_token")
    redis_url: str = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name="twitch_out", connection=redis_connection)

    event_loop = asyncio.get_running_loop()
    bot = TwitchBot(access_token=access_token, loop=event_loop)
    await asyncio.gather(sender(bot, queue), bot.start())


if __name__ == "__main__":
    asyncio.run(main())
