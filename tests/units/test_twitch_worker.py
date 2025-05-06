import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from gunlinuxbot.handlers import Event, TwitchEventHandler
from gunlinuxbot.models.twitch import TwitchMessage
from gunlinuxbot.models.myqueue import QueueMessage
from twitch_worker import (
    auf,
    command_raw_handler,
    reload_command,
    get_commands_from_dir,
    process,
)

# Constants
EXPECTED_MD_FILES = 2


@pytest.mark.asyncio
async def test_auf_command():
    # Create a mock event
    event = MagicMock(spec=TwitchMessage)
    event.author = 'test_user'

    # Create a mock post function as Callable
    post = AsyncMock()
    post.return_value = None

    # Test with post as Callable
    await auf(event, post=post)
    post.assert_called_once()
    assert '@test_user Воистину' in post.call_args[0][0]

    # Test with no post
    await auf(event, post=None)


@pytest.mark.asyncio
async def test_command_raw_handler():
    # Create a mock event
    event = MagicMock(spec=TwitchMessage)

    # Create mock data
    data = {'text': 'test message'}

    # Create a mock post function
    post = AsyncMock()
    post.return_value = None

    # Test with post as Callable and data
    await command_raw_handler(event, post=post, data=data)
    post.assert_called_once_with('test message')

    # Test with no post
    await command_raw_handler(event, post=None, data=data)

    # Test with no data
    await command_raw_handler(event, post=post, data=None)
    post.assert_called_once()  # Should still be from previous call


@pytest.mark.asyncio
async def test_process():
    # Create mock handler
    handler = MagicMock(spec=TwitchEventHandler)
    handler.handle_event = AsyncMock()

    # Create mock queue message
    queue_message = MagicMock(spec=QueueMessage)
    queue_message.data = '{"content": "test", "echo": false, "first": true, "id": "123", "channel": "test", "author": "test_user", "timestamp": "2024-01-01 00:00:00"}'

    await process(handler, queue_message)
    handler.handle_event.assert_called_once()


@pytest.mark.asyncio
async def test_reload_command():
    # Create a mock handler
    handler = MagicMock(spec=TwitchEventHandler)
    handler.clear_raw_commands = MagicMock()

    # Create a mock command directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test command file
        test_file = Path(temp_dir) / 'test.md'
        test_file.write_text('Test command content')

        # Get the reload command runner
        runner = reload_command(temp_dir, handler)

        # Test the runner
        await runner(MagicMock(spec=Event), None, None)

        # Verify the handler's clear_raw_commands was called
        handler.clear_raw_commands.assert_called_once()


@pytest.mark.asyncio
async def test_get_commands_from_dir():
    # Create a mock handler with commands attribute
    handler = MagicMock(spec=TwitchEventHandler)
    handler.clear_raw_commands = MagicMock()
    handler.commands = {}

    def mock_register(name, command):
        handler.commands[name] = command

    handler.register = mock_register

    # Create a temporary directory with test command files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test command files
        test_files = [
            'test1.md',
            'test2.md',
            'not_a_command.txt',  # This should be ignored
        ]
        for file in test_files:
            (Path(temp_dir) / file).write_text(f'Content for {file}')

        # Call the function
        get_commands_from_dir(temp_dir, handler)

        # Verify the handler's clear_raw_commands was called
        handler.clear_raw_commands.assert_called_once()

        # Verify commands were registered
        registered_commands = [k for k in handler.commands if k.startswith('!')]
        assert (
            len(registered_commands) == EXPECTED_MD_FILES
        )  # Only .md files should be registered
        assert '!test1' in registered_commands
        assert '!test2' in registered_commands
