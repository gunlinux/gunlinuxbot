import os
import asyncio
import random

from dotenv import load_dotenv
from twitchbot import TwitchBot
from event import EventHandler
from models.command import Command
from donats import DonatApi


load_dotenv()


async def run_twitch_bot(handler):
    access_token = os.environ.get("ACCESS_TOKEN", "set_Dame_token")
    event_loop = asyncio.get_running_loop()
    bot = TwitchBot(access_token=access_token, loop=event_loop, handler=handler)
    await bot.start()


async def run_test():
    while True:
        await asyncio.sleep(1)
        print(1)


async def auf(message, user, event_handler=None):
    symbols = ["AWOO", "AUF", "gunlinAuf"]
    symbols_len = random.randint(6, 12)
    out = []
    for i in range(symbols_len):
        out.append(random.choice(symbols))

    if event_handler:
        auf_str = " ".join(out)
        await event_handler.chat(f"@{user.username} Воистину {auf_str}")


async def main():
    event_handler = EventHandler()
    Command("ауф", event_handler, real_runner=auf)
    Command("gunlinauf", event_handler, real_runner=auf)
    Command("awoo", event_handler, real_runner=auf)
    Command("auf", event_handler, real_runner=auf)

    da_token = os.environ.get("DA_ACCESS_TOKEN", "set_dame_token")
    donat = DonatApi(token=da_token, handler=event_handler)

    await asyncio.gather(run_twitch_bot(event_handler), donat.run())


if __name__ == "__main__":
    asyncio.run(main())
