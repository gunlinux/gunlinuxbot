import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from gunlinuxbot.myqueue import Connection
from gunlinuxbot.twitch.twitchbot import TwitchBot


# Define the mock class
class MockRedis(Connection):
    def __init__(self):
        self.data = {}

    async def push(self, name: str, data: str) -> None:
        if name not in self.data:
            self.data[name] = []
        self.data[name].append(data)

    async def pop(self, name):
        if not self.data.get(name, []):
            return None
        return self.data[name].pop(0)

    async def llen(self, name):
        return len(self.data[name])

    async def clean(self, name):
        self.data[name] = []

    async def walk(self, name):
        return None


# Fixture to provide an instance of the mock database
@pytest.fixture
def mock_redis():
    redis = MockRedis()
    return redis


@pytest.fixture
def mock_twitch_external():
    async def mock_run(*args, **kwargs):
        for m in range(30):
            await asyncio.sleep(0.01)

    def dummy(args, **kwargs):
        return

    TwitchBot.start = mock_run
    return TwitchBot
