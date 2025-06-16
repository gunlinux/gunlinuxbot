import asyncio
import json
import os
import typing
from asyncio.subprocess import PIPE, Process
from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from gunlinuxbot.handlers import EventHandler
from gunlinuxbot.models import Event
from gunlinuxbot.utils import logger_setup
from donats.models import AlertEvent
from donats.schemas import AlertEventSchema
from local_events.commands import pay_commands  # pyright: ignore[reportMissingImports, reportUnknownVariableType]

from requeue.models import QueueMessage

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
    def __init__(self, scripts_path: str = 'local_events/scripts/'):
        # Define your valid commands and their corresponding scripts
        self.scripts_path: str = scripts_path

    async def stream_output(self, process: Process):
        while True:
            chunk = (
                await process.stdout.read(1024) if process.stdout is not None else False
            )  # Read chunks
            if not chunk:
                break
            print('STDOUT:', chunk.decode().strip())

    async def execute(self, command: str) -> bool:
        """Execute an external Python script in a subprocess"""
        print('kinda execute: %s', command)

        # Prepare the command to run the script
        cmd = ['uv', 'run', f'{self.scripts_path}{command}']

        try:
            # Create subprocess
            process: Process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )
            task = asyncio.create_task(self.stream_output(process))
            _ = task.result()

        except Exception as e:  # noqa: BLE001
            print(f'Error executing script: {e}')
            return False
        else:
            return True


class QueueConsumer(EventHandler):
    """
    Потребляет сообщения из очереди, экстрактит данный для процесса
    """

    def __init__(
        self,
        processor: CommandProcessor,
        command_config: CommandConfig,
        timeout: int = 1,
    ):
        self.processor: CommandProcessor = processor
        self.timeout: int = timeout
        self.command_config: CommandConfig = command_config
        super().__init__(sender=None, admin=None)

    @typing.override
    async def handle_event(self, event: Event) -> None:
        event = typing.cast('AlertEvent', event)
        if command := self.command_config.find(event):
            print('we found command: %s', command)
            _ = await self.processor.execute(command)

    @typing.override
    async def on_message(self, message: QueueMessage) -> QueueMessage | None:
        alert: AlertEvent = typing.cast(
            'AlertEvent', AlertEventSchema().load(json.loads(message.data))
        )
        try:
            await self.handle_event(alert)
        except Exception as e:  # noqa: BLE001
            logger.critical('cant handle message %s %s', message, e)

    @typing.override
    async def run_command(self, event: Event) -> None:
        pass


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://gunlinux.ru/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='local_events', connection=redis_connection)
        command_config: CommandConfig = CommandConfig(commands=pay_commands)  # pyright: ignore[reportUnknownArgumentType]

        processor: CommandProcessor = CommandProcessor()

        local_events_consumer: QueueConsumer = QueueConsumer(
            command_config=command_config, processor=processor
        )
        await queue.consumer(local_events_consumer.on_message)


if __name__ == '__main__':
    asyncio.run(main())
