import asyncio
from collections.abc import Callable

from twitchio import Message
from twitchio.ext import commands

from gunlinuxbot.utils import logger_setup

logger = logger_setup('twitch.twitchbot')


class TwitchBot(commands.Bot):
    def __init__(
        self,
        access_token: str,
        default_channel: str = 'gunlinux',
        loop: asyncio.AbstractEventLoop | None = None,
        handler: Callable | None = None,
    ) -> None:
        self.channels: list[str] = [default_channel]
        self.handler_function: Callable | None = handler
        super().__init__(
            token=access_token,
            prefix='?',
            initial_channels=self.channels,
            loop=loop,
        )

    async def event_ready(self) -> None:
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        logger.debug('Logged in as %s id: %s', self.nick, self.user_id)
        if not self.connected_channels:
            logger.warning('no connected channels')
            return
        for channel in self.connected_channels:
            await channel.send(f'Logged in as | {self.nick}')

    async def event_message(self, message: Message) -> None:
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            logger.debug('echo ignore')
            return

        if message and message.author and message.author.name and self.handler_function:
            await self.handler_function(message)

    async def send_message(self, message: Message) -> None:
        if not self.connected_channels:
            logger.warning('no connected channels')
            return
        for channel in self.connected_channels:
            await channel.send(message)
