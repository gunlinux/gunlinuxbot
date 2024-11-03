import asyncio
import os
import json
from dotenv import load_dotenv
from gunlinuxbot.twitch.twitchbot import TwitchBot
from gunlinuxbot.myqueue import RedisConnection, Queue
from gunlinuxbot.utils import logger_setup


logger = logger_setup('twitch_sender')


def process(event):
    data = json.loads(event)
    logger.debug('%s %s', data['event'], data['timestamp'])
    return data.get('data', {}).get('message', None)


async def sender(bot, queue):
    logger.debug("sender start")
    while True:
        new_event = await queue.pop()
        if new_event:
            mssg = process(new_event)
            if mssg:
                await bot.send_message(mssg)
        await asyncio.sleep(2)


async def main():
    load_dotenv()
    access_token = os.environ.get("ACCESS_TOKEN", "set_Dame_token")
    redis_url = os.environ.get("REDIS_URL", "redis://localhost/1")
    redis_connection = RedisConnection(redis_url, name="twitch_out")
    queue = Queue(connection=redis_connection)
    event_loop = asyncio.get_running_loop()
    bot = TwitchBot(access_token=access_token, loop=event_loop)
    await asyncio.gather(sender(bot, queue), bot.start())


if __name__ == "__main__":
    asyncio.run(main())
