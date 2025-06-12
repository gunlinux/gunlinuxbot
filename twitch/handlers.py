import logging
import typing


from twitch.models import TwitchMessage
from gunlinuxbot.handlers import EventHandler
from gunlinuxbot.models.event import Event

logger = logging.getLogger(__name__)


class TwitchEventHandler(EventHandler):
    @typing.override
    async def handle_event(self, event: Event) -> None:
        event = typing.cast('TwitchMessage', event)
        logger.debug('starting handle_message %s', event.content)
        await self.run_command(event)

    def is_admin(self, event: TwitchMessage) -> bool:
        if not event or not self.admin:
            return False
        return event.author == self.admin

    @typing.override
    async def run_command(self, event: TwitchMessage) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        logger.debug('Running command for event %s', event)
        command_to_run = None
        for command_name, command in self.commands.items():
            if event.content.startswith('$') and not self.is_admin(event):
                # ignoring admin syntax
                logger.info('ignoring admin command %s', event.content)
                continue

            if event.content.startswith(command_name.lower()):
                logger.debug('detected command: %s', command)
                command_to_run = command
                break

        if command_to_run:
            await command_to_run.run(event, post=self.chat)
