import os
import asyncio
import random
import logging

from dotenv import load_dotenv
from twitchbot import TwitchBot
from gunlinuxbot.handlers import TwitchHandler, DonatHandler, HandlerEvent
from gunlinuxbot.models.command import Command
from donats import DonatApi

load_dotenv()
logger = logging.getLogger(__name__)


async def auf(event: HandlerEvent):
    symbols = ["AWOO", "AUF", "gunlinAuf"]
    symbols_len = random.randint(6, 12)
    out = []
    for _ in range(symbols_len):
        out.append(random.choice(symbols))

    auf_str = " ".join(out)
    return f"@{event.user} Воистину {auf_str}"


async def dasha_on(event: HandlerEvent):
    from obs import dasha_show

    dasha_show()
    return f'@gunlinux, а  вот {event.user} почувствовал запах плохого кода'


async def pasha_help(event: HandlerEvent):
    from obs import pasha_help_show

    await pasha_help_show()
    return f'@gunlinux, а  вот {event.user} призвал помощь'


async def dasha_off(event: HandlerEvent):
    from obs import dasha_hide
    logger.debug('triggered command dasha_off %s', event)

    dasha_hide()


async def main():
    twitch_handler = TwitchHandler(admin="gunlinux")
    Command("ауф", twitch_handler, real_runner=auf)
    Command("gunlinauf", twitch_handler, real_runner=auf)
    Command("awoo", twitch_handler, real_runner=auf)
    Command("auf", twitch_handler, real_runner=auf)

    donats_handler = DonatHandler(admin="gunlinux")
    Command("#shitcode", donats_handler, real_runner=dasha_on)
    Command("$shitcode", twitch_handler, real_runner=dasha_off)
    Command("$help", twitch_handler, real_runner=pasha_help)
    Command("#help", donats_handler, real_runner=pasha_help)

    access_token = os.environ.get("ACCESS_TOKEN", "set_Dame_token")
    event_loop = asyncio.get_running_loop()
    bot = TwitchBot(access_token=access_token, loop=event_loop, handler=twitch_handler)
    da_token = os.environ.get("DA_ACCESS_TOKEN", "set_dame_token")
    donats_handler.set_twitch_instance(bot)
    donat = DonatApi(token=da_token, handler=donats_handler)

    await asyncio.gather(
        bot.start(),
        donat.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
