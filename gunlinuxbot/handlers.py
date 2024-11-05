from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from .utils import logger_setup

if TYPE_CHECKING:
    from .sender import Sender

logger = logger_setup('gunlinuxbot.handlers')


@dataclass
class Event:
    mssg: str
    user: str
    amount_formatted: str = ""
    alert_type: str = ""
    currency: str = ""


class Command:
    def __init__(self, name, event_handler: "EventHandler", real_runner=None):
        self.name = name
        self.event_handler: EventHandler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner

    async def run(self, event):
        logger.debug("run command %s", self.name)
        if self.real_runner is None:
            logger.debug("not implemented yet")
            return
        return await self.real_runner(event)

    def __str__(self):
        return f"<Command> {self.name}"


class EventHandler(ABC):

    def __init__(self, sender: Sender, admin=None):
        self.commands: dict[str, Command] = {}
        self.sender = sender
        self.admin = admin

    @abstractmethod
    async def handle_event(self, event: Event):
        pass

    def register(self, name, command):
        logger.debug("successfully registed command %s", name)
        self.commands[name] = command

    def set_twitch_instance(self, instance):
        logger.critical("setting instance")
        self.twitch_instance = instance

    async def run_command(self, event: Event):
        logger.debug("run_command %s", event)
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
        if self.sender is not None:
            await self.sender.send_message(mssg)
        else:
            logger.critical("cant chat sender")


class TwitchEventHandler(EventHandler):
    async def handle_event(self, event: Event):
        logger.debug("starting handle_message %s", event.mssg)
        await self.run_command(event)


class DonatEventHandler(EventHandler):
    async def handle_event(self, event: Event):
        if event.alert_type == "1":
            return await self._donation(event)

        if event.alert_type == "19":
            return await self._custom_reward(event)

        if event.alert_type == "6":
            return await self._follow(event)

        logger.critical("handle_event not implemented yet %s", event)

    async def _donation(self, event: Event):
        logger.debug("donat.event _donation")
        mssg_text = f"""{self.admin} {event.user} пожертвовал
            {event.amount_formatted} {event.currency} | {event.mssg}"""
        await self.chat(mssg_text)

    async def _follow(self, event: Event):
        logger.debug("donat.event _follow")
        mssg_text = f"@gunlinux @{event.user} started follow auf"
        await self.chat(mssg_text)

    async def _custom_reward(self, event: Event):
        logger.debug("donat.event _custom_reward %s", event)
        await self.run_command(event)
