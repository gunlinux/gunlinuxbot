import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable
import typing

from gunlinuxbot.models.event import Event
from requeue.models import QueueMessage

from .utils import logger_setup

from gunlinuxbot.sender import SenderAbc

logger = logger_setup('gunlinuxbot.handlers')
logger.setLevel(logging.DEBUG)


@runtime_checkable
class CommandRunner(Protocol):
    __name__: str

    async def __call__(
        self,
        event: Event,
        post: Awaitable[Any] | Callable[..., Any] | None = None,
        data: dict[str, str] | None = None,
    ) -> None: ...


class Command:
    def __init__(
        self,
        name: str,
        event_handler: 'EventHandler',
        data: dict[str, str] | None = None,
        real_runner: Callable[..., Any] | None = None,
    ) -> None:
        self.name: str = name
        self.event_handler: EventHandler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner
        self.data = data

    async def run(
        self, event: Event, post: Awaitable[Any] | Callable[..., Any] | None = None
    ) -> None:
        logger.debug('Running command %s for event %s', self.name, event)
        if self.real_runner is None:
            logger.warning('Command %s not implemented yet', self.name)
            return
        await self.real_runner(event, post=post, data=self.data)

    @typing.override
    def __str__(self) -> str:
        return f'<Command> {self.name}'


class EventHandler(ABC):
    def __init__(self, sender: SenderAbc | None, admin: str | None) -> None:
        self.commands: dict[str, Command] = {}
        self.sender: SenderAbc | None = sender
        self.admin = admin

    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        pass

    @abstractmethod
    async def on_message(self, message: QueueMessage) -> QueueMessage | None: ...

    def register(self, name: str, command: Command) -> None:
        logger.debug('Successfully registered command %s', name)
        self.commands[name] = command

    @abstractmethod
    async def run_command(self, event: Event) -> None: ...

    async def chat(self, mssg: str) -> None:
        if self.sender is not None:
            await self.sender.send_message(mssg)
        else:
            logger.error('Cannot send message: sender is not initialized')

    def clear_raw_commands(self) -> None:
        if not self.commands:
            return
        commands_to_remove: list[str] = []
        for command_name, command in self.commands.items():
            if (
                command.real_runner
                and command.real_runner.__name__ == 'command_raw_handler'
            ):
                commands_to_remove.append(command_name)
        for command in commands_to_remove:
            logger.info('command removed %s', command)
            _ = self.commands.pop(command)
        return
