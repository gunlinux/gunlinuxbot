import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def get_queue_stat(queue_name: str, connection: RedisConnection) -> None:
    queue: Queue = Queue(name=queue_name, connection=connection)
    logger.info('%s %s', queue, await queue.llen())
    for rec in await queue.walk():
        logger.info(rec)


async def queue_clean(queue_name: str, connection: RedisConnection) -> None:
    queue: Queue = Queue(name=queue_name, connection=connection)
    await queue.clean()


async def get_queues_stat() -> None:
    load_dotenv()
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)

    queues = ['da_events', 'twitch_mssgs', 'twitch_out']
    await asyncio.gather(
        *[get_queue_stat(queue, connection=redis_connection) for queue in queues],
    )


async def queues_clear() -> None:
    load_dotenv()
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)

    queues = ['da_events', 'twitch_mssgs', 'twitch_out']
    await asyncio.gather(
        *[queue_clean(queue, connection=redis_connection) for queue in queues],
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Описание твоей программы',
        prog=f'{sys.argv[0]}',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Подкоманда 'clear'
    clear_parser = subparsers.add_parser('clear', help='Очистить очереди')
    clear_parser.set_defaults(func=lambda: asyncio.run(queues_clear()))

    # Подкоманда 'stat'
    stat_parser = subparsers.add_parser('stat', help='Получить статистику очередей')
    stat_parser.set_defaults(func=lambda: asyncio.run(get_queues_stat()))

    args = parser.parse_args()
    args.func()


if __name__ == '__main__':
    main()
