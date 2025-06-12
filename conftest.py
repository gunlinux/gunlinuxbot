import asyncio
import json
from pathlib import Path
import typing
import logging
import os

import pytest

from requeue.schemas import QueueMessageSchema
from requeue.requeue import Queue
from requeue.rredis import Connection
from gunlinuxbot.twitch.twitchbot import TwitchBot

if typing.TYPE_CHECKING:
    from requeue.models import QueueMessage


logging.getLogger('asyncio').setLevel(logging.WARNING)

os.environ['TESTING'] = '1'


# Define the mock class
class MockRedis(Connection):
    def __init__(self):
        self.data: dict[str, typing.Any] = {}

    @typing.override
    async def _connect(self) -> None:
        pass

    @typing.override
    async def _close(self) -> None:
        pass

    @typing.override
    async def push(self, name: str, data: str) -> None:
        if name not in self.data:
            self.data[name] = []
        self.data[name].append(data)

    @typing.override
    async def pop(self, name: str) -> str:
        if not self.data.get(name, []):
            return ''
        return self.data[name].pop(0)

    @typing.override
    async def llen(self, name: str) -> int:
        return len(self.data[name])

    @typing.override
    async def clean(self, name: str):
        self.data[name] = []

    @typing.override
    async def walk(self, name: str) -> list[str]:
        _ = name
        return []


# Fixture to provide an instance of the mock database
@pytest.fixture
def mock_redis():
    return MockRedis()


@pytest.fixture
def mock_twitch_external():
    async def mock_run(*args, **kwargs):
        _, _ = args, kwargs
        for _ in range(30):
            await asyncio.sleep(0.01)

    TwitchBot.start = mock_run
    return TwitchBot


def load_test_queue(name: str):
    @pytest.fixture
    async def load_test_queue_from_data(mock_redis: Connection):
        async with mock_redis as connection:
            queue = Queue(name=name, connection=connection)
            with Path.open(
                Path(f'tests/data/{name}.json'), 'r', encoding='utf-8'
            ) as test_data:
                data = json.load(test_data)
            for item in data:
                item['data'] = json.dumps(item['data'])
                message: QueueMessage = typing.cast(
                    'QueueMessage', QueueMessageSchema().load(item)
                )
                await queue.push(message)
            return queue

    return load_test_queue_from_data


load_da_events = load_test_queue('da_events')
