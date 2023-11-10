from models.user import User
from models.mssg import Mssg
from models.command import Command


class EventHandler:
    users: set[User] = set()
    mssgs: list[Mssg] = list()
    commands: dict = dict()
    twitch_instance = None

    def __init__(self):
        pass

    def __str__(self):
        return f'{self.users} {self.mssgs}'

    def get_or_add_user(self, id, username):
        for user in self.users:
            if user.id == id:
                return user
        user = User(id=id, username=username)
        self.users.add(user)
        return user

    async def handle_event(self, message):
        print(f'starting hanlde_message {message}')
        chatter = message.author
        content = message.content
        print(type(message))
        if not chatter:
            return
        user = self.get_or_add_user(chatter.id,chatter.name)
        mssg = Mssg(id=message.id, mssg=message.content, user_id=chatter.id)
        user.new_mssg()
        self.mssgs.append(mssg)
        print(f'{user.username}: {mssg.mssg}')
        for command_name, command in self.commands.items():
            if message.content.startswith(command_name):
                print(f'detected command: {command}')
                await command.run(mssg, user)

    def show_users(self):
        print('users:')
        for user in self.users:
            print(user)

    def register(self, name, Command):
        print(f'successfully registed command {name}')
        self.commands[name] = Command
        print(self.commands)

    async def chat(self, mssg):
        await self.twitch_instance.send_message(mssg)
        print(f'send_mssg_to_chat {mssg}')

    def set_twitch_instance(self, instance):
        self.twitch_instance = instance


def auf(message, user, event_hander=None):
    if event_handler:
        event_handler.chat(f'@{user.username} Воистину ауф')


if __name__ == '__main__':
    event_handler = EventHandler()
    echo_command = Command('!ауф',  event_handler, real_runner=auf)
    messages = [
        {'userid': 1, 'username': 'gunlinux', 'mssg': 'hello', 'id': 1},
        {'userid': 2, 'username': 'onehundredprecentass', 'mssg': '!ауф', 'id': 2},
        {'userid': 1, 'username': 'gunlinux', 'mssg': 'сяп', 'id': 3},
        {'userid': 1, 'username': 'gunlinux', 'mssg': '!ауф', 'id': 4},
        {'userid': 1, 'username': 'gunlinux', 'mssg': '!echo hello', 'id': 4},
        {'userid': 3, 'username': 'wigust', 'mssg': 'Pog', 'id': 5},
    ]


    for message in messages:
        event_handler.handle_event(message)

    event_handler.show_users()

