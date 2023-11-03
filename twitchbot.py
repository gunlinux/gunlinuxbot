from twitchio.ext import commands


class TwitchBot(commands.Bot):

    def __init__(self, access_token, channels=None, default_channel='gunlinux'):
        if channels is None:
            channels = [default_channel]
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=access_token, prefix='?', initial_channels=channels)

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
        if message.echo:
            print('echo ignore')
            return

        # Print the contents of our message to console...
        print(message.content)
        # print(dir(message))

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)




