import asyncio
import os

from gunlinuxbot.handlers import Command

from twitch.handlers import TwitchEventHandler
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from sender.sender import Sender
from gunlinuxbot.utils import logger_setup
from commander import get_commands_from_dir, reload_command
from commander.commands import auf

logger = logger_setup('twitch_worker')


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
