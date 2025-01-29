import asyncio
import json
import os
import random
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from gunlinuxbot.handlers import Command, Event, EventHandler, TwitchEventHandler
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitch_worker')


async def process(handler: EventHandler, data: str) -> None:
    process_data: dict = json.loads(data)
    payload_data = process_data.get('data', {})
    mssg = payload_data.get('content', '')
    user = payload_data.get('author', {}).get('name')
    if not mssg or not user:
        return
    event: Event = Event(mssg=mssg, user=user)
    await handler.handle_event(event)
    logger.critical('something happened %s', event)
    await asyncio.sleep(1)
    return


async def auf(event: Event, post: Awaitable[Any] | Callable | None = None, data: dict[str, str] | None = None)-> str:
    logger.critical('auf %s ', data)
    symbols = ['AWOO', 'AUF', 'gunlinAuf']
    symbols_len = random.randint(6, 12) #  noqa: S311
    out = [random.choice(symbols) for _ in range(symbols_len)] # noqa: S311

    auf_str = ' '.join(out)
    logger.critical('%s %s', auf_str, event)
    temp =  f'@{event.user} Воистину {auf_str}'
    logger.critical('auf end %s', temp)

    if post:
        return await post(temp)
    return temp


async def command_raw_handler(event: Event, post: Awaitable[Any] | Callable | None = None, data: dict[str, str] | None = None) -> str:
    logger.critical('command handler %s %s', data, event)

    if post:
        return await post('')
    return ''


def get_commands_from_dir(command_dir: str, twitch_handler: TwitchEventHandler) -> None:
    # Get all files matching the '*.md' pattern
    command_path = Path.cwd() / command_dir
    markdown_files = [f for f in command_path.iterdir() if f.is_file() and f.suffix == '.md']

    for file in markdown_files:
        # Construct the full path to each file
        # Open the file and read its contents
        data = {}
        with Path.open(file, 'r'):
            data['name'] = Path(file).stem
            data['text'] = file.read_text()

            print('registred command %s ', data)
            Command(data['name'], twitch_handler, real_runner=command_raw_handler, data=data)


async def main() -> Awaitable[None]:
    load_dotenv()
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url, name='twitch_mssgs')
    redis_sender_connection = RedisConnection(redis_url, name='twitch_out')

    queue = Queue(connection=redis_connection)
    sender_queue = Queue(connection=redis_sender_connection)
    sender = Sender(queue=sender_queue)
    twitch_handler = TwitchEventHandler(sender=sender, admin='gunlinux')

    Command('ауф', twitch_handler, real_runner=auf)
    Command('gunlinAuf', twitch_handler, real_runner=auf)
    Command('awoo', twitch_handler, real_runner=auf)
    Command('auf', twitch_handler, real_runner=auf)

    command_dir = os.environ.get('COMMAND_DIR', './commands/')
    get_commands_from_dir(command_dir, twitch_handler)
    await asyncio.sleep(1)

    while True:
        new_event = await queue.pop()
        if new_event:
            await process(handler=twitch_handler, data=new_event)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
