import logging


logger = logging.getLogger(name=__name__)

from donats.handlers import DonatEventHandler
from requeue.requeue import Queue
from gunlinuxbot.sender import DummySender


async def process(handler, data):
    _ = handler
    logger.debug('process start %s', data)


async def test_real_events(load_da_events: Queue):
    queue = load_da_events
    await queue.pop()

    sender: DummySender = DummySender(
        queue_name='twitch_out', connection=queue.connection
    )
    donat_handler: DonatEventHandler = DonatEventHandler(
        sender=sender,
        admin='gunlinux',
    )

    for _ in range(2):
        new_event = await queue.pop()
        if new_event:
            await process(handler=donat_handler, data=new_event)
