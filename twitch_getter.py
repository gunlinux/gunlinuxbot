import asyncio
import os
import json
from datetime import datetime
from typing import Callable, TYPE_CHECKING, Any, Coroutine
from dotenv import load_dotenv
from gunlinuxbot.twitch.twitchbot import TwitchBot
from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.utils import logger_setup
if TYPE_CHECKING:
    from twitchio.message import Message


logger = logger_setup('twitch_sender')


async def init_process(queue: Queue) -> Callable[[Message], Coroutine[Any, Any, None]]:
    process_queue: Queue = queue

    async def process_mssg(message: Message) -> None:
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
        await process_queue.push(json.dumps(payload))
    return process_mssg


async def main() -> None:
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
