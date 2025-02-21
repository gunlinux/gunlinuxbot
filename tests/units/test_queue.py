import json
import pytest
from datetime import datetime
from gunlinuxbot.myqueue import Queue


async def test_queue(mock_redis):
    queue = Queue(name="test_queue", connection=mock_redis)
    dummy_stamp = datetime.timestamp(datetime.now())

    payload1 = {
        "event": "Test event 1",
        "data": json.dumps({"kinda": 1}),
        "timestamp": dummy_stamp,
        "source": "test_queue",
    }
    payload2 = {
        "event": "Test event 2",
        "data": json.dumps({"kinda": 1}),
        "timestamp": dummy_stamp,
        "source": "test_queue",
    }
    await queue.push(json.dumps(payload1))
    assert await queue.llen() == 1
    await queue.push(json.dumps(payload2))
    assert await queue.llen() == 2  # noqa: PLR2004
    assert json.loads(await queue.pop()) == payload1
    assert await queue.llen() == 1
    assert json.loads(await queue.pop()) == payload2
    assert await queue.llen() == 0
    assert await queue.pop() is None


async def test_queue_opts(mock_redis):
    queue = Queue(name="test_queue", connection=mock_redis)
    dummy_stamp = datetime.timestamp(datetime.now())

    payload1 = {
        "event": "Test event 1",
        "data": json.dumps({"kinda": 1}),
        "timestamp": dummy_stamp,
        "source": "test_queue",
    }
    payload2 = {
        "event": "Test event 2",
        "data": json.dumps({"kinda": 1}),
        "timestamp": dummy_stamp,
        "source": "test_queue",
    }
    await queue.push(json.dumps(payload1))
    assert await queue.llen() == 1
    await queue.push(json.dumps(payload2))
    assert await queue.llen() == 2  # noqa: PLR2004
    await queue.clean()
    assert await queue.llen() == 0
    assert await queue.pop() is None
