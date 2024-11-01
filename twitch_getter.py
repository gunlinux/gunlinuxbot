import asyncio
import os
import logging
import json
from datetime import datetime

from dotenv import load_dotenv
from gunlinuxbot.twitch.twitchbot import TwitchBot
from gunlinuxbot.myqueue import RedisConnection, Queue


logger = logging.getLogger(__name__)


async def init_process(queue):
    queue = queue

    async def process_mssg(message):
        if not message:
            return
        payload = {
            "event": "twitch_message",
            "timestamp": datetime.timestamp(datetime.now()),
            "data": {
                "content": message.content,
                "author": {
                    "name": message.author.name,
                    #  "channel": str(message.author.channel),
                },
                "echo": message.echo,
                "first": message.first,
                "id": message.id,
            },
        }
        logger.critical(payload)
        await queue.push(json.dumps(payload))
    return process_mssg


async def main():
    load_dotenv()
    access_token = os.environ.get("ACCESS_TOKEN", "set_Dame_token")
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="twitch_mssgs")
    queue = Queue(connection=redis_connection)
    event_loop = asyncio.get_running_loop()
    handler = await init_process(queue)
    bot = TwitchBot(access_token=access_token, loop=event_loop, handler=handler)
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
