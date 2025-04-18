import argparse
import asyncio
import os
import sys

from gunlinuxbot.myqueue import Queue, RedisConnection
from gunlinuxbot.utils import logger_setup

logger = logger_setup(__name__)


async def get_queues_stat() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)

    queues_names = ['da_events', 'twitch_mssgs', 'twitch_out', 'bs_donats']
    queues = [Queue(name=name, connection=redis_connection) for name in queues_names]

    for queue in queues:
        logger.info('queue: %s (%s)', queue.name, await queue.llen())


async def queues_clear() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    redis_connection: RedisConnection = RedisConnection(redis_url)

    queues_names = ['da_events', 'twitch_mssgs', 'twitch_out', 'bs_donats']
    queues = [Queue(name=name, connection=redis_connection) for name in queues_names]

    for queue in queues:
        logger.info('clearing queue: %s', queue.name)
        await queue.clean()


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
