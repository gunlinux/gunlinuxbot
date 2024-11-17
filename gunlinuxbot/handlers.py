from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from .utils import logger_setup

if TYPE_CHECKING:
    from .sender import Sender

logger = logger_setup('gunlinuxbot.handlers')


class DonationAlertTypes(Enum):
    DONATION = '1'
    CUSTOM_REWARD = '19'
    FOLLOW = '6'


@dataclass
class Event:
    mssg: str
    user: str
    amount_formatted: str = ''
    alert_type: str = ''
    currency: str = ''


class Command:
    def __init__(
        self,
        name: str,
        event_handler: 'EventHandler',
        real_runner: Callable | None = None,
    ) -> None:
        self.name: str = name
        self.event_handler: EventHandler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner

    async def run(self, event: Event) -> None:
        logger.debug('run command %s', self.name)
        if self.real_runner is None:
            logger.debug('not implemented yet')
            return
        await self.real_runner(event)

    def __str__(self) -> str:
        return f'<Command> {self.name}'


class EventHandler(ABC):
    def __init__(self, sender: 'Sender', admin: str | None) -> None:
        self.commands: dict[str, Command] = {}
        self.sender = sender
        self.admin = admin

    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        pass

    def register(self, name: str, command: Callable) -> None:
        logger.debug('successfully registed command %s', name)
        self.commands[name] = command

    """
    def set_twitch_instance(self, instance) -> None:
        logger.critical('setting instance')
        self.twitch_instance = instance
    """

    def is_admin(self, event: Event) -> bool:
        if not event:
            return None
        return event.user != self.admin

    async def run_command(self, event: Event) -> None:
        logger.debug('run_command %s', event)
        for command_name, command in self.commands.items():
            if event.mssg.startswith('$') and not self.is_admin(event):
                # ignoring admin syntax
                logger.info('ignoring admin command %s', event.mssg)
                continue

            if event.mssg.startswith(command_name):
                logger.debug('detected command: %s', command)
                result = await command.run(event)
                if result:
                    await self.chat(result)

    async def chat(self, mssg: str) -> None:
        if self.sender is not None:
            await self.sender.send_message(mssg)
        else:
            logger.critical('cant chat sender')


class TwitchEventHandler(EventHandler):
    async def handle_event(self, event: Event) -> None:
        logger.debug('starting handle_message %s', event.mssg)
        await self.run_command(event)


class DonatEventHandler(EventHandler):
    async def handle_event(self, event: Event) -> None:
        if event.alert_type == DonationAlertTypes.DONATION:
            return await self._donation(event)

        if event.alert_type == DonationAlertTypes.CUSTOM_REWARD:
            return await self._custom_reward(event)

        if event.alert_type == DonationAlertTypes.FOLLOW:
            return await self._follow(event)

        logger.critical('handle_event not implemented yet %s', event)
        return None

    async def _donation(self, event: Event) -> None:
        logger.debug('donat.event _donation')
        mssg_text = f"""{self.admin} {event.user} пожертвовал
            {event.amount_formatted} {event.currency} | {event.mssg}"""
        await self.chat(mssg_text)

    async def _follow(self, event: Event) -> None:
        logger.debug('donat.event _follow')
        mssg_text = f'@gunlinux @{event.user} started follow auf'
        await self.chat(mssg_text)

    async def _custom_reward(self, event: Event) -> None:
        logger.debug('donat.event _custom_reward %s', event)
        await self.run_command(event)
