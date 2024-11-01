import logging

from twitchio.ext import commands

logger = logging.getLogger(__name__)


class TwitchBot(commands.Bot):

    def __init__(
        self,
        access_token,
        default_channel="gunlinux",
        loop=None,
        handler=None,
    ):
        self.channels = [default_channel]
        self.handler_function = handler
        self.debug = False
        super().__init__(
            token=access_token, prefix="?", initial_channels=self.channels, loop=loop
        )

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        logger.debug("Logged in as %s id: %s", self.nick, self.user_id)
        if self.connected_channels:
            for channel in self.connected_channels:
                await channel.send(f"Logged in as | {self.nick}")

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo and not self.debug:
            logger.debug("echo ignore")
            return

        if message and message.author and message.author.name:
            if self.handler_function:
                await self.handler_function(message)

    async def send_message(self, message):
        if self.connected_channels:
            for channel in self.connected_channels:
                await channel.send(message)
