from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.command import Command

import abc
import logging

logger = logging.getLogger(__name__)


@dataclass
class HandlerEvent:
    mssg: str
    user: str
    amount_formatted: str = ''
    alert_type: str = ''
    currency: str = ''


class EventHandler(abc.ABC):

    def __init__(self, instance=None, admin=None):
        self.commands: dict[str, Command] = {}
        self.twitch_instance = instance
        self.admin = admin

    @abc.abstractmethod
    async def handle_event(self, event: HandlerEvent):
        pass

    def register(self, name, command):
        logger.debug("successfully registed command %s", name)
        self.commands[name] = command

    def set_twitch_instance(self, instance):
        logger.critical('setting instance')
        self.twitch_instance = instance

    async def run_command(self, event: HandlerEvent):
        logger.debug('run_command %s', event)
        for command_name, command in self.commands.items():
            if event.mssg.startswith("$") and event.user != self.admin:
                # ignoring admin syntax
                logger.info("ignoring admin command %s", event.mssg)
                continue

            if event.mssg.startswith(command_name):
                logger.debug("detected command: %s", command)
                result = await command.run(event)
                if result:
                    await self.chat(result)

    async def chat(self, mssg):
        if self.twitch_instance is not None:
            await self.twitch_instance.send_message(mssg)
        else:
            logger.critical('cant chat no instance')


class TwitchHandler(EventHandler):
    async def handle_event(self, event: HandlerEvent):
        logger.debug(f"starting hanlde_message {event.mssg}")
        await self.run_command(event)


class DonatHandler(EventHandler):
    async def handle_event(self, event: HandlerEvent):
        if event.alert_type == "1":
            return await self._donation(event)

        if event.alert_type == "19":
            return await self._custom_reward(event)

        if event.alert_type == "6":
            return await self._follow(event)

        logger.critical("handle_event not implemented yet %s", event)

    async def _donation(self, event: HandlerEvent):
        mssg_text = f"""{self.admin} {event.user} пожертвовал
            {event.amount_formatted} {event.currency} | {event.mssg}"""
        await self.chat(mssg_text)

    async def _follow(self, event: HandlerEvent):
        mssg_text = f"@gunlinux @{event.user} started follow auf"
        await self.chat(mssg_text)

    async def _custom_reward(self, event: HandlerEvent):
        logger.critical('_custom_reward %s', event)
        await self.run_command(event)
