import asyncio
import os
from collections.abc import Callable, Coroutine
import typing
import json
from socketio import exceptions as socketio_exceptions

from dotenv import load_dotenv

from gunlinuxbot.donats.donats import DonatApi
from gunlinuxbot.handlers import Event
from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.schemas.myqueue import QueueMessageSchema
from gunlinuxbot.utils import logger_setup

if typing.TYPE_CHECKING:
    from gunlinuxbot.models.myqueue import QueueMessage
    from gunlinuxbot.models.donats import AlertEvent

logger = logger_setup('donats_getter')


async def init_process(
    queue: Queue,
) -> Callable[[Event], Coroutine[typing.Any, typing.Any, None]]:
    work_queue: Queue = queue

    async def process_mssg(message: Event) -> None:
        logger.critical(message)
        message = typing.cast('AlertEvent', message)
        message_dict = message.serialize()
        message_id = message_dict.get('id', None)
        if queue.last_id and queue.last_id == message_id:
            # doesnt repeat itself
            logger.critical('dont repeat itself')
            await asyncio.sleep(0.1)
            return
        queue.last_id = message_id
        message_dict.get('id', None)
        payload = {
            'event': 'da_message',
            'data': json.dumps(message_dict),
        }
        logger.debug('new process_mssg da_events %s', payload)
        new_message: QueueMessage = typing.cast(
            'QueueMessage', QueueMessageSchema().load(payload)
        )
        await work_queue.push(new_message)

    return process_mssg


async def main() -> None:
    load_dotenv()
    access_token = os.environ.get('DA_ACCESS_TOKEN', 'set_Dame_token')
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url)
    queue = Queue(name='da_events', connection=redis_connection)

    handler = await init_process(queue)
    bot = DonatApi(token=access_token, handler=handler)
    try:
        while True:
            await bot.run()
    except socketio_exceptions.ConnectionError:
        logger.critical('Connection error we are reconnecting')


if __name__ == '__main__':
    asyncio.run(main())
