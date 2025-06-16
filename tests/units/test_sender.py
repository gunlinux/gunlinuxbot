from requeue.requeue import Queue
from sender.sender import Sender
from requeue.schemas import QueueMessageSchema
from requeue.models import QueueMessage
from requeue.rredis import Connection
from dataclasses import asdict


async def test_sender(mock_redis: Connection):
    async with mock_redis as connection:
        queue: Queue = Queue(name='twitch_out', connection=connection)
        sender = Sender(queue_name='twitch_out', connection=connection)
        tmp_mssg = 'okface привет как ты'
        await sender.send_message(tmp_mssg)
        result = await queue.pop()
        assert isinstance(result, QueueMessage)
        assert result.event == 'mssg'
        assert result.source == ''
        assert result.data == tmp_mssg
        assert not QueueMessageSchema().validate(asdict(result))


async def test_custom_sender(mock_redis):
    queue: Queue = Queue(name='twitch_out', connection=mock_redis)
    sender = Sender(
        queue_name='twitch_out',
        connection=mock_redis,
        source='test_source',
    )
    tmp_mssg = 'okface привет как ты'
    await sender.send_message(tmp_mssg)
    result = await queue.pop()
    assert isinstance(result, QueueMessage)
    assert result.event == 'mssg'
    assert result.source == 'test_source'
    assert result.data == tmp_mssg


async def test_custom_sender_with_source(mock_redis):
    queue: Queue = Queue(name='twitch_out', connection=mock_redis)
    sender = Sender(queue_name='twitch_out', connection=mock_redis)
    tmp_mssg = 'okface привет как ты'
    await sender.send_message(tmp_mssg, source='test_source')
    result = await queue.pop()
    assert isinstance(result, QueueMessage)
    assert result.event == 'mssg'
    assert result.source == 'test_source'
    assert result.data == tmp_mssg
