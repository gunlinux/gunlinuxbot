import asyncio
import sys
import os

from requeue.rredis import RedisConnection
from sender.sender import Sender


async def main() -> None:
    mssg = sys.argv[1]
    redis_url: str = os.environ.get('REDIS_URL', 'redis://gunlinux.ru/1')
    async with RedisConnection(redis_url) as redis_connection:
        sender = Sender(queue_name=mssg, connection=redis_connection)
        await sender.send_message("hello darkness my old friend")


if __name__ == '__main__':
    asyncio.run(main())
