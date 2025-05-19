import asyncio
import os
from asyncio.subprocess import PIPE


from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup
from local_events.commands import pay_commands

from gunlinuxbot.models.myqueue import QueueMessage

logger = logger_setup('local_events')


class CommandProcessor:
    def __init__(self, command_map: dict[str, dict[str, str | int]]):
        # Define your valid commands and their corresponding scripts
        self.command_map = command_map

    async def execute_script(self, script_path):
        """Execute an external Python script in a subprocess"""

        # Prepare the command to run the script
        cmd = ['python', script_path]

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )

            # Wait for the subprocess to finish
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                print(f'Script failed with error: {stderr.decode().strip()}')
                return False
            print(f'Script output: {stdout.decode().strip()}')

        except Exception as e:  # noqa: BLE001
            print(f'Error executing script: {e}')
            return False
        else:
            return True


def process(data: QueueMessage) -> str | None:
    logger.debug('%s process %s', __name__, data.event)
    return data.data


async def local_command_worker(queue: Queue) -> None:
    logger.debug('sender start')
    command_processor = CommandProcessor(command_map=pay_commands)
    await command_processor.execute_script('lol')

    while True:
        new_event = await queue.pop()
        if new_event:
            process(new_event)
        await asyncio.sleep(1)


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='twitch_out', connection=redis_connection)
    await local_command_worker(queue)


if __name__ == '__main__':
    asyncio.run(main())
