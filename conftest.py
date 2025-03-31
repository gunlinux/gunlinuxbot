import asyncio
import json
from pathlib import Path
from typing import Any
from collections.abc import Mapping

import pytest

from gunlinuxbot.myqueue import Connection, Queue
from gunlinuxbot.twitch.twitchbot import TwitchBot


# Define the mock class
class MockRedis(Connection):
    def __init__(self):
        self.data: dict[str, Any] = {}

    async def push(self, name: str, data: str | Mapping) -> None:
        if name not in self.data:
            self.data[name] = []
        self.data[name].append(data)

    async def pop(self, name):
        if not self.data.get(name, []):
            return None
        return self.data[name].pop(0)

    async def llen(self, name):
        return len(self.data[name])

    async def clean(self, name: str):
        self.data[name] = []

    async def walk(self, name: str) -> list[Any]:
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
    async def load_test_queue_from_data(mock_redis):
        queue = Queue(name=name, connection=mock_redis)
        with Path.open(
            Path(f'tests/data/{name}.json'), 'r', encoding='utf-8'
        ) as test_data:
            data = json.load(test_data)
        for item in data:
            await queue.push(json.dumps(item))
        return queue

    return load_test_queue_from_data


load_da_events = load_test_queue('da_events')
