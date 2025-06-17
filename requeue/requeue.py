import typing
import json
import logging
import asyncio
from collections.abc import Callable, Awaitable

if typing.TYPE_CHECKING:
    from requeue.rredis import Connection
from requeue.models import QueueMessageStatus, QueueMessage
from requeue.schemas import QueueMessageSchema

logger = logging.getLogger(__name__)


class Queue:
    def __init__(self, name: str, connection: 'Connection', max_retry: int = 5) -> None:
        self.name: str = name
        self.last_id: str | None = None
        self.connection: Connection = connection
        self.max_retry: int = max_retry

    async def push(self, data: QueueMessage) -> None:
        if data.status == QueueMessageStatus.PROCESSING:
            data.retry += 1
            data.status = QueueMessageStatus.WAITING

        if data.retry > self.max_retry:
            logger.critical('message retried more than %s %s', self.max_retry, data)
            return

        queue_message_dict = data.to_serializable_dict()
        await self.connection.push(self.name, json.dumps(queue_message_dict))

    async def pop(self) -> QueueMessage | None:
        temp_data: str = await self.connection.pop(self.name)
        if not temp_data:
            return None
        message: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(json.loads(temp_data))
        )
        message.status = QueueMessageStatus.PROCESSING
        return message

    async def consumer(
        self, on_message: Callable[[QueueMessage], Awaitable[QueueMessage | None]]
    ) -> None:
        while True:
            await asyncio.sleep(1)
            new_event: QueueMessage | None = await self.pop()
            if new_event is None:
                continue
            result = await on_message(new_event)
            if not result:
                continue
            await self.push(result)

    async def llen(self) -> int | None:
        return await self.connection.llen(self.name)

    async def walk(self) -> list[typing.Any]:
        return await self.connection.walk(self.name)

    async def clean(self) -> None:
        return await self.connection.clean(self.name)

    @typing.override
    def __str__(self) -> str:
        return f'<Queue {self.name}>'
