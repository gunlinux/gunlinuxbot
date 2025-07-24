from collections.abc import Callable, Awaitable
from pathlib import Path
import typing
from gunlinuxbot.handlers import EventHandler, Command
from gunlinuxbot.models import Event
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def command_raw_handler(
    event: Event, **kwargs: dict[str, typing.Any]
) -> str | None:
    logger.debug('RAW command handler %s', event)
    if 'text' not in kwargs:
        return None
    return typing.cast('str', kwargs.get('text', ''))


def reload_command(
    command_dir: str, twitch_handler: EventHandler
) -> Callable[[Event], Awaitable[None]] | None:
    async def reload_command_inner(*args: typing.Any, **kwargs: typing.Any):
        _, _ = args, kwargs
        nonlocal twitch_handler, command_dir
        get_commands_from_dir(command_dir, twitch_handler)

    return reload_command_inner


def get_commands_from_dir(command_dir: str, twitch_handler: EventHandler) -> None:
    # Get all files matching the '*.md' pattern
    twitch_handler.clear_raw_commands()
    command_path = Path.cwd() / command_dir
    markdown_files = [
        f for f in command_path.iterdir() if f.is_file() and f.suffix == '.md'
    ]

    for file in markdown_files:
        # Construct the full path to each file
        # Open the file and read its contents
        data: dict[str, typing.Any] = {}
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
