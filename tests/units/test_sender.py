from gunlinuxbot.myqueue import Queue
from gunlinuxbot.sender import Sender
from gunlinuxbot.schemas.queue import QueueMessage, QueueMessageSchema
from dataclasses import asdict
import datetime


async def test_sender(mock_redis):
    queue: Queue = Queue(name="twitch_out", connection=mock_redis)
    sender = Sender(queue=queue)
    tmp_mssg = "okface привет как ты"
    await sender.send_message(tmp_mssg)
    result = await queue.pop()
    assert isinstance(result, QueueMessage)
    assert result.event == 'mssg'
    assert result.source == ''
    assert result.data == tmp_mssg
    result.timestamp = datetime.datetime.now().isoformat()
    assert not QueueMessageSchema().validate(asdict(result))


async def test_custom_sender(mock_redis):
    queue: Queue = Queue(name="twitch_out", connection=mock_redis)
    sender = Sender(queue=queue, source="test_source")
    tmp_mssg = "okface привет как ты"
    await sender.send_message(tmp_mssg)
    result = await queue.pop()
    assert isinstance(result, QueueMessage)
    assert result.event == 'mssg'
    assert result.source == 'test_source'
    assert result.data == tmp_mssg
