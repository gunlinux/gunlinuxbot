class Command:
    event_handler: None
    name: str
    real_runner: None

    def __init__(self, name, event_handler, real_runner=None):
        print(f'command registed {name}')
        self.name = name
        self.event_handler = event_handler
        self.event_handler.register(self.name, self)
        self.real_runner = real_runner

    async def run(self, message, user):
        print(f'run command {self.name}')
        if self.real_runner is None:
            print('not implemented yet')
            return
        return await self.real_runner(message, user, self.event_handler)

    def __str__(self):
        return f'<Command> {self.name}'

