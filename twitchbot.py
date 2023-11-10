from twitchio.ext import commands


class TwitchBot(commands.Bot):
    handler_function = None
    debug = False

    def __init__(self, access_token, channels=None, default_channel='gunlinux', loop=None, handler=None, debug=False):
        if channels is None:
            channels = [default_channel]
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        if handler:
            self.handler_function = handler.handle_event
            handler.twitch_instance = self
        self.debug = debug
        super().__init__(token=access_token, prefix='?', initial_channels=channels, loop=loop)

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')
        if self.connected_channels:
            for channel in self.connected_channels:
                await channel.send(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo and not self.debug:
            print('echo ignore')
            return

        print(message.content)

        if self.handler_function:
            await self.handler_function(message)

    async def send_message(self, message):
        if self.connected_channels:
            for channel in self.connected_channels:
                await channel.send(message)
