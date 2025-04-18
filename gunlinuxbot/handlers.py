import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from gunlinuxbot.models.donats import AlertEvent, DonationTypes
from gunlinuxbot.models.event import Event
from gunlinuxbot.models.twitch import TwitchMessage

from .utils import logger_setup

if TYPE_CHECKING:
    from .sender import Sender

logger = logger_setup('gunlinuxbot.handlers')
logger.setLevel(logging.DEBUG)


class DonationAlertTypes(Enum):
    DONATION = 1
    CUSTOM_REWARD = 19
    FOLLOW = 6


class Command:
    def __init__(
        self,
        name: str,
        event_handler: 'EventHandler',
        data: dict[str, str] | None = None,
        real_runner: Callable | None = None,
    ) -> None:
        self.name: str = name
        self.event_handler: EventHandler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner
        self.data = data

    async def run(
        self, event: Event, post: Awaitable[Any] | Callable | None = None
    ) -> None:
        logger.debug('Running command %s for event %s', self.name, event)
        if self.real_runner is None:
            logger.warning('Command %s not implemented yet', self.name)
            return
        await self.real_runner(event, post=post, data=self.data)

    def __str__(self) -> str:
        return f'<Command> {self.name}'


class EventHandler(ABC):
    def __init__(self, sender: 'Sender', admin: str | None) -> None:
        self.commands: dict[str, Command] = {}
        self.sender: Sender = sender
        self.admin = admin

    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        pass

    def register(self, name: str, command: Command) -> None:
        logger.debug('Successfully registered command %s', name)
        self.commands[name] = command

    def is_admin(self, event: TwitchMessage) -> bool:
        if not event or not self.admin:
            return False
        return event.author == self.admin

    async def run_command(self, event: TwitchMessage) -> None:
        logger.debug('Running command for event %s', event)
        for command_name, command in self.commands.items():
            if event.content.startswith('$') and not self.is_admin(event):
                # ignoring admin syntax
                logger.info('ignoring admin command %s', event.content)
                continue

            if event.content.startswith(command_name.lower()):
                logger.debug('detected command: %s', command)
                await command.run(event, post=self.chat)

    async def chat(self, mssg: str) -> None:
        if self.sender is not None:
            await self.sender.send_message(mssg)
        else:
            logger.error('Cannot send message: sender is not initialized')


class TwitchEventHandler(EventHandler):
    async def handle_event(self, event: Event) -> None:
        event = cast('TwitchMessage', event)
        logger.debug('starting handle_message %s', event.content)
        await self.run_command(event)


class DonatEventHandler(EventHandler):
    async def send_donate(self, event: AlertEvent):
        message = {
            'value': int(event.amount_formatted),
            'name': event.username,
        }
        await self.sender.send_message(
            message=json.dumps(message), source='donat_handler', queue_name='bs_donats'
        )

    async def handle_event(self, event: Event) -> None:  # pyright: ignore[reportRedeclaration]
        event = cast('AlertEvent', event)
        if isinstance(event.alert_type, DonationTypes):
            alert_type = int(event.alert_type.value)
        else:
            alert_type: int = int(cast('str', event.alert_type))
        event: AlertEvent = cast('AlertEvent', event)
        if alert_type == DonationAlertTypes.DONATION.value:
            await self._donation(event)
            return

        if alert_type == DonationAlertTypes.CUSTOM_REWARD.value:
            await self._custom_reward(event)
            return

        if alert_type == DonationAlertTypes.FOLLOW.value:
            await self._follow(event)
            return

        logger.warning('handle_event not implemented yet %s', event)
        return

    async def _donation(self, event: AlertEvent) -> None:
        logger.info('donat.event _donation')
        if event.username is None:
            event.username = 'anonym'
        mssg_text = f"""{self.admin} {event.username} пожертвовал
            {event.amount_formatted} {event.currency} | {event.message}"""
        await self.send_donate(event)
        await self.chat(mssg_text)

    async def _follow(self, event: AlertEvent) -> None:
        logger.info('donat.event _follow')
        mssg_text = f'@gunlinux @{event.username} started follow auf'
        await self.chat(mssg_text)

    async def _custom_reward(self, event: AlertEvent) -> None:
        logger.info('donat.event _custom_reward %s', event)
        await self.run_command(event)

    async def run_command(self, event: AlertEvent) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        logger.debug('Running command for event %s', event)
        # test it
        for command_name, command in self.commands.items():
            if event.message.startswith('$'):
                # ignoring admin syntax
                logger.info('ignoring admin command %s')
                continue

            if event.message.startswith(command_name.lower()):
                logger.debug('detected command: %s', command)
                await command.run(event, post=self.chat)
