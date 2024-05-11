import logging
from ..handlers import EventHandler

logger = logging.getLogger(__name__)


class Command:
    def __init__(self, name, event_handler: EventHandler, real_runner=None):
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
