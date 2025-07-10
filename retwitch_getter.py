import asyncio
import os
import typing

from dotenv import load_dotenv

from retwitch.token import TokenManager
from retwitch.bot import BotClient, ChannelBotClient
from retwitch.schemas import Event
from gunlinuxbot.utils import logger_setup
from dataclasses import asdict


import json
from collections.abc import Callable, Awaitable

from requeue.requeue import Queue
from requeue.rredis import RedisConnection, Connection
from requeue.schemas import QueueMessageSchema

if typing.TYPE_CHECKING:
    from requeue.models import QueueMessage


logger = logger_setup('retwitch')


async def init_process(
    redis_connection: Connection,
) -> Callable[[Event], Awaitable[None]]:
    process_queue: Queue = Queue(name='retwitch_mssgs', connection=redis_connection)
    local_events: Queue = Queue(name='retwitch_events', connection=redis_connection)

    async def process_mssg(event: Event) -> None:
        logger.info('processsing event: %s', event)
        payload: QueueMessage = typing.cast(
            'QueueMessage',
            QueueMessageSchema().load(
                {
                    'event': 'retwitch_message',
                    'data': json.dumps(asdict(event)),
                },
            ),
        )
        await process_queue.push(payload)
        await local_events.push(payload)

    return process_mssg


async def main():
    load_dotenv()
    client_id: str = os.getenv('RECLIENT_ID', '')
    client_secret: str = os.getenv('RECLIENT_SECRET', '')
    owner_id: str = os.getenv('REOWNER_ID', '')
    bot_id: str = os.getenv('REBOT_ID', '')
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')

    token_manager = TokenManager(client_id=client_id, client_secret=client_secret)
    token_manager.load_real_token()
    await token_manager.refresh_token()
    token_manager.save_real_token()

    channel_token_manager: TokenManager = TokenManager(
        client_id=client_id,
        client_secret=client_secret,
        token_file='channels_tokens.json',  # noqa: S106
    )
    channel_token_manager.load_real_token()
    await channel_token_manager.refresh_token()
    channel_token_manager.save_real_token()

    async with RedisConnection(redis_url) as redis_connection:
        handler = await init_process(redis_connection=redis_connection)

        bot = BotClient(
            token_manager=token_manager,
            client_id=client_id,
            user_id=bot_id,
            broadcaster_user_id=owner_id,
        )
        bot_channel = ChannelBotClient(
            token_manager=channel_token_manager,
            client_id=client_id,
            user_id=bot_id,
            broadcaster_user_id=owner_id,
        )
        await asyncio.gather(bot.run(handler=handler), bot_channel.run(handler=handler))


if __name__ == '__main__':
    asyncio.run(main())
