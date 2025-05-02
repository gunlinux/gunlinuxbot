import asyncio
import json
import os
import random
from collections.abc import Callable, Mapping, Awaitable
from pathlib import Path
from typing import cast, Any, TYPE_CHECKING

from gunlinuxbot.handlers import (
    Command,
    Event,
    EventHandler,
    TwitchEventHandler,
    CommandRunner,
)
from gunlinuxbot.models.myqueue import QueueMessage
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.sender import Sender
from gunlinuxbot.utils import logger_setup
from gunlinuxbot.schemas.twitch import TwitchMessageSchema

if TYPE_CHECKING:
    from gunlinuxbot.models.twitch import TwitchMessage

logger = logger_setup('twitch_worker')


async def process(handler: EventHandler, queue_message: QueueMessage) -> None:
    twitch_event: TwitchMessage = cast(
        'TwitchMessage',
        TwitchMessageSchema().load(
            cast('Mapping', json.loads(queue_message.data)),
        ),
    )
    await handler.handle_event(twitch_event)
    logger.debug('something happened %s', twitch_event)
    await asyncio.sleep(1)


async def auf(
    event: Event,
    post: Awaitable[Any] | Callable | None = None,
    data: dict[str, str] | None = None,
) -> None:
    event = cast('TwitchMessage', event)
    logger.debug('auf %s ', data)
    symbols = ['AWOO', 'AUF', 'gunlinAuf']
    symbols_len = random.randint(6, 12)  #  noqa: S311
    out = [random.choice(symbols) for _ in range(symbols_len)]  # noqa: S311

    auf_str = ' '.join(out)
    temp = f'@{event.author} Воистину {auf_str}'

    if post:
        if isinstance(post, Awaitable):
            await post
        else:
            await post(temp)


async def command_raw_handler(
    event: Event,
    post: Awaitable[Any] | Callable | None = None,
    data: dict[str, str] | None = None,
) -> None:
    event = cast('TwitchMessage', event)
    logger.debug('RAW command handler %s %s', data, event)

    if post and data is not None:
        if isinstance(post, Awaitable):
            await post
        else:
            await post(data['text'])


def reload_command(command_dir, twitch_handler: TwitchEventHandler) -> CommandRunner:
    async def reload_command_inner(
        event: Event,  # noqa: ARG001
        post: Awaitable[Any] | Callable | None = None,  # noqa: ARG001
        data: dict[str, str] | None = None,  # noqa: ARG001
    ) -> None:
        nonlocal twitch_handler, command_dir
        get_commands_from_dir(command_dir, twitch_handler)

    reload_command_inner.__name__ = 'reload_command_inner'
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
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='twitch_mssgs', connection=redis_connection)
    sender = Sender(queue_name='twitch_out', connection=redis_connection)
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
    await asyncio.sleep(1)

    while True:
        new_event: QueueMessage | None = await queue.pop()
        if new_event is not None:
            await process(handler=twitch_handler, queue_message=new_event)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    asyncio.run(main())
