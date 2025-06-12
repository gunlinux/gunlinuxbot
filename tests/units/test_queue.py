import json
from typing import TYPE_CHECKING
import typing
from requeue.rredis import Connection
from requeue.schemas import QueueMessageSchema
from requeue.models import QueueMessageStatus
from requeue.requeue import Queue

if TYPE_CHECKING:
    from requeue.models import QueueMessage


async def test_queue(mock_redis: Connection):
    async with mock_redis as connection:
        queue = Queue(name='test_queue', connection=connection)

        payload1 = {
            'event': 'Test event 1',
            'data': json.dumps({'kinda': 1}),
            'source': 'test_queue',
            'retry': 0,
            'status': QueueMessageStatus.WAITING.value,
        }
        payload2 = {
            'event': 'Test event 2',
            'data': json.dumps({'kinda': 2}),
            'source': 'test_queue',
            'retry': 0,
            'status': QueueMessageStatus.WAITING.value,
        }
        message_one: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload1)
        )
        message_two: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload2)
        )
        await queue.push(message_one)
        assert await queue.llen() == 1
        await queue.push(message_two)
        assert await queue.llen() == 2  # noqa: PLR2004

        data_from_queue_1: QueueMessage | None = await queue.pop()
        assert data_from_queue_1 is not None
        payload1['status'] = QueueMessageStatus.PROCESSING.value
        assert data_from_queue_1.to_serializable_dict() == payload1
        assert await queue.llen() == 1
        data_from_queue_2: QueueMessage | None = await queue.pop()
        assert data_from_queue_2 is not None
        payload2['status'] = QueueMessageStatus.PROCESSING.value
        assert data_from_queue_2.to_serializable_dict() == payload2
        assert await queue.llen() == 0
        assert await queue.pop() is None


async def test_queue_opts(mock_redis: Connection):
    async with mock_redis as connection:
        queue = Queue(name='test_queue', connection=connection)

        payload1 = {
            'event': 'Test event 1',
            'data': json.dumps({'kinda': 1}),
            'source': 'test_queue',
        }
        payload2 = {
            'event': 'Test event 2',
            'data': json.dumps({'kinda': 1}),
            'source': 'test_queue',
        }
        message_one: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload1)
        )
        message_two: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload2)
        )

        await queue.push(message_one)
        assert await queue.llen() == 1
        await queue.push(message_two)
        assert await queue.llen() == 2  # noqa: PLR2004
        await queue.clean()
        assert await queue.llen() == 0
        assert await queue.pop() is None


async def test_retry(mock_redis: Connection):
    async with mock_redis as connection:
        queue = Queue(name='test_queue', connection=connection)

        payload1 = {
            'event': 'Test event 1',
            'data': json.dumps({'kinda': 1}),
            'source': 'test_queue',
            'retry': 0,
            'status': QueueMessageStatus.WAITING.value,
        }
        message_one: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload1)
        )
        await queue.push(message_one)
        assert await queue.llen() == 1
        for _ in range(10):
            data_from_queue_1 = await queue.pop()
            if data_from_queue_1:
                await queue.push(data_from_queue_1)
        assert await queue.llen() == 0
        assert await queue.pop() is None
