from typing import cast, TYPE_CHECKING, Any


from abc import ABC, abstractmethod

from .myqueue import Connection, Queue
from .utils import logger_setup
from gunlinuxbot.schemas.myqueue import QueueMessageSchema

if TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage

logger = logger_setup('gunlinuxbot.sender')


class SenderAbc(ABC):
    @abstractmethod
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None: ...

    @abstractmethod
    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None: ...


class Sender(SenderAbc):
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None:
        self.connection = connection
        self.queue = Queue(name=queue_name, connection=connection)
        self.source = source

    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None:
        payload: dict[str, Any] = {
            'event': 'mssg',
            'data': message,
            'source': source or self.source,
        }
        new_message: QueueMessage = cast(
            'QueueMessage', QueueMessageSchema().load(payload)
        )
        if not queue_name:
            await self.queue.push(new_message)
            return
        await Queue(name=queue_name, connection=self.connection).push(new_message)


class DummySender(SenderAbc):
    def __init__(
        self,
        queue_name: str,
        connection: Connection,
        source: str = '',
    ) -> None:
        self.connection = connection
        self.queue_name = queue_name
        self.source = source

    async def send_message(
        self,
        message: str,
        source: str = '',
        queue_name: str = '',
    ) -> None:
        _ = source, queue_name
        logger.debug('send_message to %s "%s"', self.queue_name, message)
