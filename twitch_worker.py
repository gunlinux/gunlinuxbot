import asyncio
import os
import random
from collections.abc import Callable
from pathlib import Path
import typing

from gunlinuxbot.handlers import Command, Event
from twitch.handlers import TwitchEventHandler
from twitch.models import TwitchMessage
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from sender.sender import Sender
from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitch_worker')


async def auf(
    event: TwitchMessage,
    post: Callable | None = None,
    data: dict[str, str] | None = None,
) -> str:
    logger.debug('auf %s ', data)
    symbols = ['AWOO', 'AUF', 'gunlinAuf']
    symbols_len = random.randint(6, 12)  #  noqa: S311
    out = [random.choice(symbols) for _ in range(symbols_len)]  # noqa: S311

    auf_str = ' '.join(out)
    temp = f'@{event.author} Воистину {auf_str}'

    if post:
        return await post(temp)
    return temp


async def command_raw_handler(
    event: Event,
    post: Callable | None = None,
    data: dict[str, str] | None = None,
) -> str:
    logger.debug('RAW command handler %s %s', data, event)

    if post and data is not None:
        return await post(data['text'])
    return ''


def reload_command(command_dir, twitch_handler: TwitchEventHandler) -> Callable:
    async def reload_command_inner(*args: typing.Any, **kwargs: typing.Any):
        _, _ = args, kwargs
        nonlocal twitch_handler, command_dir
        get_commands_from_dir(command_dir, twitch_handler)

    return reload_command_inner


def get_commands_from_dir(command_dir: str, twitch_handler: TwitchEventHandler) -> None:
    # Get all files matching the '*.md' pattern
    twitch_handler.clear_raw_commands()
    command_path = Path.cwd() / command_dir
    markdown_files = [
        f for f in command_path.iterdir() if f.is_file() and f.suffix == '.md'
    ]

    for file in markdown_files:
        # Construct the full path to each file
        # Open the file and read its contents
        data = {}
        with Path.open(file, 'r'):
            data['name'] = Path(file).stem
            data['text'] = file.read_text()

            logger.info('registred command from file %s ', data)
            Command(
                f'!{data["name"]}',
                twitch_handler,
                real_runner=command_raw_handler,
                data=data,
            )


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    async with RedisConnection(redis_url) as conn:
        queue: Queue = Queue(name='twitch_mssgs', connection=conn)
        sender = Sender(queue_name='twitch_out', connection=conn)
        twitch_handler = TwitchEventHandler(
            sender=sender,
            admin='gunlinux',
        )

        Command('ауф', twitch_handler, real_runner=auf)
        Command('gunlinAuf', twitch_handler, real_runner=auf)
        Command('awoo', twitch_handler, real_runner=auf)
        Command('auf', twitch_handler, real_runner=auf)

        command_dir = os.environ.get('COMMAND_DIR', './commands/')
        get_commands_from_dir(command_dir, twitch_handler)
        reload_command_runner = reload_command(command_dir, twitch_handler)
        Command('$reload', twitch_handler, real_runner=reload_command_runner)
        await queue.consumer(twitch_handler.on_message)


if __name__ == '__main__':
    asyncio.run(main())
