import argparse
import asyncio
import os
import sys
from typing import NoReturn

from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def get_queue_stat(queue: str) -> dict:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url, name=queue)
    queue = Queue(connection=redis_connection)
    logger.info('%s %s', queue, await queue.llen())
    for rec in await queue.walk():
        logger.info(rec)
    await redis_connection.redis.aclose()


async def queue_clean(queue: str) -> dict:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection = RedisConnection(redis_url, name=queue)
    queue = Queue(connection=redis_connection)
    await queue.clean()
    await redis_connection.redis.aclose()


async def get_queues_stat() -> None:
    load_dotenv()
    queues = ['da_events', 'twitch_mssgs', 'twitch_out']
    await asyncio.gather(*[get_queue_stat(queue) for queue in queues])


async def queues_clear() -> None:
    load_dotenv()
    queues = ['da_events', 'twitch_mssgs', 'twitch_out']
    await asyncio.gather(*[queue_clean(queue) for queue in queues])


def main() -> NoReturn:
    parser = argparse.ArgumentParser(
        description="Описание твоей программы",
        prog=f"{sys.argv[0]}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Подкоманда 'clear'
    clear_parser = subparsers.add_parser("clear", help="Очистить очереди")
    clear_parser.set_defaults(func=lambda: asyncio.run(queues_clear()))

    # Подкоманда 'stat'
    stat_parser = subparsers.add_parser("stat", help="Получить статистику очередей")
    stat_parser.set_defaults(func=lambda: asyncio.run(get_queues_stat()))

    args = parser.parse_args()
    args.func()


if __name__ == "__main__":
    main()
