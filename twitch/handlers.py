from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)


@dataclass
class HandlerEvent:
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

    def __init__(self, sender: "Sender", admin=None):
        self.commands: dict[str, Command] = {}
        self.sender = sender
        self.admin = admin

    @abstractmethod
    async def handle_event(self, event: HandlerEvent):
        pass

    def register(self, name, command):
        logger.debug("successfully registed command %s", name)
        self.commands[name] = command

    def set_twitch_instance(self, instance):
        logger.critical("setting instance")
        self.twitch_instance = instance

    async def run_command(self, event: HandlerEvent):
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
    async def handle_event(self, event: HandlerEvent):
        print(f"starting handle_message {event.mssg}")
        await self.run_command(event)