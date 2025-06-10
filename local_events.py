import asyncio
import json
import os
import typing
from asyncio.subprocess import PIPE

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup
from gunlinuxbot.models.donats import AlertEvent
from gunlinuxbot.schemas.donats import AlertEventSchema
from local_events.commands import pay_commands  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

if typing.TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage

logger = logger_setup('local_events')


class CommandConfig:
    def __init__(self, commands: list[dict[str, typing.Any]]) -> None:
        self.commands: list[dict[str, typing.Any]] = commands
        self.currencices: dict[str, float] = {
            'USD': 80,
            'RUB': 1,
            'EUR': 90,
        }

    def _get_final_amount(self, amount: float, currency: str) -> float:
        if point := self.currencices.get(currency):
            return point * amount
        raise ValueError

    def find(self, alert: AlertEvent) -> str | None:
        for command in self.commands:
            if (
                command['name'] in alert.message
                and self._get_final_amount(alert.amount, alert.currency)
                > command['price']
            ):
                return command['command']
        print('command not fouind', alert)
        return None


class CommandProcessor:
    def __init__(self, scripts_path='local_events/scripts/'):
        # Define your valid commands and their corresponding scripts
        self.scripts_path = scripts_path

    async def stream_output(self, process):
        while True:
            chunk = await process.stdout.read(1024)  # Read chunks
            if not chunk:
                break
            print('STDOUT:', chunk.decode().strip())

    async def execute(self, command):
        """Execute an external Python script in a subprocess"""
        print('kinda execute: %s', command)

        # Prepare the command to run the script
        cmd = ['uv', 'run', f'{self.scripts_path}{command}']

        try:
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )
            task = asyncio.create_task(self.stream_output(process))
            return process, task

        except Exception as e:  # noqa: BLE001
            print(f'Error executing script: {e}')
            return False
        else:
            return True


class QueueConsumer:
    """
    Потребляет сообщения из очереди, экстрактит данный для процесса
    """

    def __init__(
        self,
        queue: Queue,
        processor: CommandProcessor,
        commmand_config: CommandConfig,
        timeout: int = 1,
    ):
        self.queue: Queue = queue
        self.processor: CommandProcessor = processor
        self.timeout: int = timeout
        self.commmand_config: CommandConfig = commmand_config

    async def run(self):
        while True:
            new_event: QueueMessage | None = await self.queue.pop()
            if not new_event:
                await asyncio.sleep(self.timeout)
                continue
            alert: AlertEvent = typing.cast(
                'AlertEvent', AlertEventSchema().load(json.loads(new_event.data))
            )
            if command := self.commmand_config.find(alert):
                await self.processor.execute(command)


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)
    queue: Queue = Queue(name='local_events', connection=redis_connection)
    commmand_config: CommandConfig = CommandConfig(commands=pay_commands)
    processor: CommandProcessor = CommandProcessor()

    await QueueConsumer(
        queue=queue, commmand_config=commmand_config, processor=processor
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
