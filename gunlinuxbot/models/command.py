from ..handlers import EventHandler


class Command:
    def __init__(self, name, event_handler: EventHandler, real_runner=None):
        print(f'command registed {name}')
        self.name = name
        self.event_handler: EventHandler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner

    async def run(self, event):
        print(f'run command {self.name}')
        if self.real_runner is None:
            print('not implemented yet')
            return
        return await self.real_runner(event)

    def __str__(self):
        return f'<Command> {self.name}'
