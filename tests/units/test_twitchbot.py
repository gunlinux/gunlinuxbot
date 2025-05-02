import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from gunlinuxbot.twitch.twitchbot import TwitchBot, TwitchBotSender, TwitchBotGetter
from twitchio import Message

# Constants
TEST_TOKEN = 'placeholder_token'  # noqa: S105 # This is a test token used only in tests


@pytest.mark.asyncio
async def test_twitchbot_initialization():
    # Test basic initialization
    bot = TwitchBot(access_token=TEST_TOKEN)
    assert bot.channels == ['gunlinux']
    assert bot.handler_function is None
    assert bot._prefix == '?'  # noqa: SLF001

    # Test with custom channel and handler
    handler = AsyncMock()
    bot = TwitchBot(
        access_token=TEST_TOKEN, default_channel='test_channel', handler=handler
    )
    assert bot.channels == ['test_channel']
    assert bot.handler_function == handler


@pytest.mark.asyncio
async def test_twitchbot_sender():
    # Create a mock bot
    bot = TwitchBotSender(access_token=TEST_TOKEN)

    # Mock connected channels
    channel1 = MagicMock()
    channel1.send = AsyncMock()
    channel2 = MagicMock()
    channel2.send = AsyncMock()

    # Patch the connected_channels property
    with patch.object(
        bot.__class__, 'connected_channels', property(lambda _: [channel1, channel2])
    ):
        # Test sending message
        await bot.send_message('test message')
        channel1.send.assert_called_once_with('test message')
        channel2.send.assert_called_once_with('test message')

    # Test with no connected channels
    with patch.object(bot.__class__, 'connected_channels', property(lambda _: [])):
        await bot.send_message('test message')  # Should log warning but not raise error


@pytest.mark.asyncio
async def test_twitchbot_getter_event_ready():
    # Create a mock bot
    bot = TwitchBotGetter(access_token=TEST_TOKEN)

    # Mock bot properties
    with (
        patch.object(bot.__class__, 'nick', property(lambda _: 'test_bot')),
        patch.object(bot.__class__, 'user_id', property(lambda _: '123')),
        patch.object(bot.__class__, 'connected_channels', property(lambda _: [])),
    ):
        # Test with no connected channels
        await bot.event_ready()  # Should log warning but not raise error

    # Test with connected channel
    channel = MagicMock()
    channel.send = AsyncMock()
    with (
        patch.object(bot.__class__, 'nick', property(lambda _: 'test_bot')),
        patch.object(bot.__class__, 'user_id', property(lambda _: '123')),
        patch.object(
            bot.__class__, 'connected_channels', property(lambda _: [channel])
        ),
    ):
        # Test event_ready
        await bot.event_ready()
        channel.send.assert_called_once_with('Logged in as | test_bot')


@pytest.mark.asyncio
async def test_twitchbot_getter_event_message():
    # Create a mock bot with handler
    handler = AsyncMock()
    bot = TwitchBotGetter(access_token=TEST_TOKEN, handler=handler)

    # Test with echo message
    message = MagicMock(spec=Message)
    message.echo = True
    await bot.event_message(message)
    handler.assert_not_called()

    # Test with valid message
    message = MagicMock(spec=Message)
    message.echo = False
    message.author = MagicMock()
    message.author.name = 'test_user'
    await bot.event_message(message)
    handler.assert_called_once_with(message)

    # Test with message but no author
    message = MagicMock(spec=Message)
    message.echo = False
    message.author = None
    await bot.event_message(message)
    assert handler.call_count == 1  # Should not have been called again

    # Test with message but no author name
    message = MagicMock(spec=Message)
    message.echo = False
    message.author = MagicMock()
    message.author.name = None
    await bot.event_message(message)
    assert handler.call_count == 1  # Should not have been called again
