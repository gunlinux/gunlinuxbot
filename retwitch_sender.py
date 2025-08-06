import asyncio
import os
import typing

from dotenv import load_dotenv

from retwitch.token import TokenManager
from retwitch.bot import SenderBotClient
from retwitch.reqs import TwitchAccessError
from gunlinuxbot.utils import logger_setup


from requeue.requeue import Queue
from requeue.rredis import RedisConnection

from requeue.models import QueueMessage


logger = logger_setup('retwitch')


async def init_process(bot: SenderBotClient) -> typing.Any:
    async def process(message: QueueMessage) -> None:
        logger.debug('%s process %s', __name__, message.event)
        if message.data:
            try:
                await bot.send_message(message.data)
            except TwitchAccessError as e:
                await bot.token_manager.refresh_token()
                logger.critical('twitch access error', exc_info=e)
            await asyncio.sleep(5)

    return process


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

    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='twitch_out', connection=redis_connection)
        bot = SenderBotClient(
            token_manager=token_manager,
            client_id=client_id,
            user_id=bot_id,
            broadcaster_user_id=owner_id,
        )

        process = await init_process(bot)
        await queue.consumer(process)


if __name__ == '__main__':
    asyncio.run(main())
