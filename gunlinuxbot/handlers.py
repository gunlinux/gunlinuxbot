from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, NoReturn

import aiohttp

from .utils import logger_setup

if TYPE_CHECKING:
    from .sender import Sender

logger = logger_setup('gunlinuxbot.handlers')


class DonationAlertTypes(Enum):
    DONATION = 1
    CUSTOM_REWARD = 19
    FOLLOW = 6


async def send_donate(value: float, name: str) -> dict | None:
    url = "http://127.0.0.1:6016/donate"
    data = {
        "date": datetime.now().isoformat(),
        "value": value,
        "name": name,
    }
    headers = {
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            return await response.json()


@dataclass
class Event:
    mssg: str
    user: str
    id: int = 0
    amount_formatted: str = ''
    alert_type: str = ''
    currency: str = ''


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

    async def run(self, event: Event, post: Awaitable[Any] | Callable | None = None) -> None:
        logger.debug('run command %s %s ', self.name, event)
        if self.real_runner is None:
            logger.debug('not implemented yet')
            return
        await self.real_runner(event, post=post, data=self.data)

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

    def register(self, name: str, command: Command) -> None:
        logger.debug('successfully registed command %s', name)
        self.commands[name] = command

    """
    def set_twitch_instance(self, instance) -> None:
        logger.critical('setting instance')
        self.twitch_instance = instance
    """

    def is_admin(self, event: Event) -> bool:
        if not event:
            return False
        return event.user != self.admin

    async def run_command(self, event: Event) -> NoReturn:
        logger.debug('run_command %s', event)
        for command_name, command in self.commands.items():
            if event.mssg.startswith('$') and not self.is_admin(event):
                # ignoring admin syntax
                logger.info('ignoring admin command %s', event.mssg)
                continue

            if event.mssg.startswith(command_name.lower()):
                logger.debug('detected command: %s', command)
                await command.run(event, post=self.chat)

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
        alert_type: int = int(event.alert_type)
        logger.critical('alert type %s %s %s', alert_type, type(alert_type), event)
        logger.critical('alert type don %s', DonationAlertTypes.DONATION)
        if alert_type == DonationAlertTypes.DONATION.value:
            await self._donation(event)
            return

        if alert_type == DonationAlertTypes.CUSTOM_REWARD.value:
            await self._custom_reward(event)
            return

        if alert_type == DonationAlertTypes.FOLLOW.value:
            await self._follow(event)
            return

        logger.critical('handle_event not implemented yet %s', event)
        return

    async def _donation(self, event: Event) -> None:
        logger.debug('donat.event _donation')
        if event.user is None:
            event.user = 'anonym'
        mssg_text = f"""{self.admin} {event.user} пожертвовал
            {event.amount_formatted} {event.currency} | {event.mssg}"""
        logger.critical('_donation %s %s', event.amount_formatted, type(event.amount_formatted))
        await send_donate(int(event.amount_formatted), event.user)
        await self.chat(mssg_text)

    async def _follow(self, event: Event) -> None:
        logger.debug('donat.event _follow')
        mssg_text = f'@gunlinux @{event.user} started follow auf'
        await self.chat(mssg_text)

    async def _custom_reward(self, event: Event) -> None:
        logger.debug('donat.event _custom_reward %s', event)
        await self.run_command(event)
