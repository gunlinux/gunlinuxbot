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
from retwitch.schemas import (
    RetwitchEventSchema,
    RetwitchEvent,
    promote_event,
    EventType,
)

from requeue.models import QueueMessage

logger = logger_setup('local_events')


def alertevent_from_twitch(event: RetwitchEvent) -> AlertEvent | None:
    message = event.event_type.name
    if event.event_type == EventType.CUSTOM_REWARD:
        message = event.event.get('title', message)
    return AlertEvent(
        id=0,
        alert_type=0,
        billing_system='RETWITCH',
        username=event.user_name,
        amount=0,
        amount_formatted='',
        currency='POINTS',
        date_created='',
        message=message,
        _is_test_alert=False,
    )


class CommandConfig:
    def __init__(self, lcommands: list[dict[str, typing.Any]]) -> None:
        self.commands: list[dict[str, typing.Any]] = lcommands
        self.currencices: dict[str, float] = {
            'USD': 80,
            'RUB': 1,
            'EUR': 90,
            'POINTS': 1,
        }

    def _get_final_amount(self, amount: float, currency: str) -> float:
        if point := self.currencices.get(currency):
            return point * amount
        raise ValueError

    def find(self, alert: AlertEvent) -> str | None:
        for command in self.commands:
            # donation alerts donate :D
            if (
                command['name'] in alert.message
                and self._get_final_amount(alert.amount, alert.currency)
                > command['price']
                and command['type'] == 'donate'
                and alert.billing_system != 'TWITCH'
            ):
                return command['command']
            print(alert.message)
            print(command['name'])
            if (
                alert.billing_system == 'RETWITCH'
                and command['type'] == 'twitch'
                and command['name'] == alert.message
            ):
                return command['command']
        print('command not found by name', alert)
        if alert.currency != 'RUB':
            return None
        for command in self.commands:
            # donation alerts donate :D
            if command['type'] == 'bycash' and command['price'] == int(alert.amount):
                logger.critical('found command by price %s', alert)
                return command['command']
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
        logger.critical('kinda execute: %s', command)
        logger.critical('%s %s', self.scripts_path, command)

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
            logger.critical('Error executing script: %s', e)
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
            logger.info('we found command: %s', command)
            _ = await self.processor.execute(command)
            return
        logger.critical('cant find a command %s', event)

    @typing.override
    async def on_message(self, message: QueueMessage) -> QueueMessage | None:
        if message.event == 'da_message':
            return await self._on_message_da(message)
        if message.event == 'retwitch_message':
            return await self._on_message_twitch(message)
        return None

    async def _on_message_da(self, message: QueueMessage) -> QueueMessage | None:
        try:
            alert: AlertEvent = typing.cast(
                'AlertEvent', AlertEventSchema().load(json.loads(message.data))
            )
            if alert.billing_system == 'TWITCH':
                # ignore twich messages
                return
        except Exception as e:  # noqa: BLE001
            logger.critical('cant handle event %s', e)
            return
        logger.info('start to handle_event %s', alert)
        await self.handle_event(alert)

    async def _on_message_twitch(self, message: QueueMessage) -> QueueMessage | None:
        try:
            twitch_event: RetwitchEvent = typing.cast(
                'RetwitchEvent', RetwitchEventSchema().load(json.loads(message.data))
            )
        except Exception as e:  #  noqa: BLE001
            logger.critical('cant load schema of message %s', e)
            return
        if twitch_event.event_type == 'channel.chat.message':
            logger.critical('ignore chat')
            return
        twitch_event = promote_event(twitch_event)
        alert = alertevent_from_twitch(twitch_event)
        if alert:
            await self.handle_event(alert)
        return

    @typing.override
    async def run_command(self, event: Event) -> None:
        pass


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://gunlinux.ru/1')
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='local_events', connection=redis_connection)
        command_config: CommandConfig = CommandConfig(pay_commands)  # pyright: ignore[reportUnknownArgumentType]

        processor: CommandProcessor = CommandProcessor()

        local_events_consumer: QueueConsumer = QueueConsumer(
            command_config=command_config, processor=processor
        )
        print('yam yam yam')
        await queue.consumer(local_events_consumer.on_message)


if __name__ == '__main__':
    asyncio.run(main())
