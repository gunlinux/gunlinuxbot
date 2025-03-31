from gunlinuxbot.handlers import DonatEventHandler, EventHandler
from gunlinuxbot.myqueue import Queue
from gunlinuxbot.sender import DummySender


async def process(handler, data):
    _ = handler
    print(f'process start {data}')


async def test_real_events(load_da_events: Queue):
    queue = load_da_events
    await queue.pop()

    sender = DummySender(queue_name='twitch_out', connection=None)
    donat_handler: EventHandler = DonatEventHandler(
        sender=sender,
        admin='gunlinux',
    )

    for _ in range(2):
        new_event = await queue.pop()
        if new_event:
            await process(handler=donat_handler, data=new_event)
