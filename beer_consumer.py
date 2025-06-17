import asyncio
import datetime
import json
import os
import typing

import aiohttp
from aiohttp.client_exceptions import ClientConnectorError

from requeue.requeue import Queue
from requeue.rredis import RedisConnection
from donats.models import AlertEvent
from donats.schemas import AlertEventSchema
from gunlinuxbot.utils import logger_setup

from requeue.models import QueueMessage

logger = logger_setup('twitch_sender')


class BeerConsumer:
    def __init__(self, donate_url: str) -> None:
        self.donate_url = donate_url

    async def on_message(self, message: QueueMessage) -> None:
        logger.debug('%s process %s', __name__, message.data)
        alert_event: AlertEvent = typing.cast(
            'AlertEvent', AlertEventSchema().load(json.loads(message.data))
        )
        stat_data = self._from_alert_event_to_bs(alert_event)

        payload = {
            'date': datetime.datetime.now().isoformat(),
            'value': stat_data.get('value', 0),
            'name': stat_data.get('name', ''),
        }
        headers = {
            'Content-Type': 'application/json',
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.donate_url, json=payload, headers=headers
                ) as response:
                    return await response.json()
            except ClientConnectorError:
                logger.warning('cant connect to bs service')

    def _from_alert_event_to_bs(self, event: AlertEvent) -> dict[str, int | str | None]:
        print(event)
        message: dict[str, int | str | None] = {
            'value': int(event.amount_formatted),
            'name': event.username,
        }
        return message


async def main() -> None:
    redis_url: str = os.environ.get('REDIS_URL', 'redis://localhost/1')
    beer_donate_url: str = os.environ.get('BEER_URL', 'http://127.0.0.1:6016/donate')
    beer_consumer: BeerConsumer = BeerConsumer(donate_url=beer_donate_url)
    async with RedisConnection(redis_url) as redis_connection:
        queue: Queue = Queue(name='bs_donats', connection=redis_connection)
        await queue.consumer(on_message=beer_consumer.on_message)


if __name__ == '__main__':
    asyncio.run(main())
