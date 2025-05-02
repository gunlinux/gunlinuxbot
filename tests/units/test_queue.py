from dataclasses import asdict
import json
from typing import TYPE_CHECKING
from gunlinuxbot.myqueue import Queue
from gunlinuxbot.schemas.myqueue import QueueMessageSchema

if TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage


async def test_queue(mock_redis):
    queue = Queue(name='test_queue', connection=mock_redis)
    from gunlinuxbot.models.myqueue import QueueMessageStatus

    payload1 = {
        'event': 'Test event 1',
        'data': json.dumps({'kinda': 1}),
        'source': 'test_queue',
        'retry': 0,
        'status': QueueMessageStatus.WAITING,
    }
    payload2 = {
        'event': 'Test event 2',
        'data': json.dumps({'kinda': 2}),
        'source': 'test_queue',
        'retry': 0,
        'status': QueueMessageStatus.WAITING,
    }
    message_one: QueueMessage = QueueMessageSchema().load(payload1)
    message_two: QueueMessage = QueueMessageSchema().load(payload2)
    await queue.push(message_one)
    assert await queue.llen() == 1
    await queue.push(message_two)
    assert await queue.llen() == 2  # noqa: PLR2004

    data_from_queue_1 = await queue.pop()
    payload1['status'] = QueueMessageStatus.PROCESSING
    assert asdict(data_from_queue_1) == payload1
    assert await queue.llen() == 1
    data_from_queue_2 = await queue.pop()
    payload2['status'] = QueueMessageStatus.PROCESSING
    assert asdict(data_from_queue_2) == payload2
    assert await queue.llen() == 0
    assert await queue.pop() is None


async def test_queue_opts(mock_redis):
    queue = Queue(name='test_queue', connection=mock_redis)

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
    message_one: QueueMessage = QueueMessageSchema().load(payload1)
    message_two: QueueMessage = QueueMessageSchema().load(payload2)

    await queue.push(message_one)
    assert await queue.llen() == 1
    await queue.push(message_two)
    assert await queue.llen() == 2  # noqa: PLR2004
    await queue.clean()
    assert await queue.llen() == 0
    assert await queue.pop() is None


async def test_retry(mock_redis):
    queue = Queue(name='test_queue', connection=mock_redis)
    from gunlinuxbot.models.myqueue import QueueMessageStatus

    payload1 = {
        'event': 'Test event 1',
        'data': json.dumps({'kinda': 1}),
        'source': 'test_queue',
        'retry': 0,
        'status': QueueMessageStatus.WAITING,
    }
    message_one: QueueMessage = QueueMessageSchema().load(payload1)
    await queue.push(message_one)
    assert await queue.llen() == 1
    for _ in range(10):
        data_from_queue_1 = await queue.pop()
        if data_from_queue_1:
            await queue.push(data_from_queue_1)
    assert await queue.llen() == 0
    assert await queue.pop() is None
