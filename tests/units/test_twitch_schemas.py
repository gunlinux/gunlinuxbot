import pytest
from datetime import datetime
from unittest.mock import Mock
from marshmallow.exceptions import ValidationError

from gunlinuxbot.schemas.twitch import (
    SendMessageSchema,
    TwitchMessageSchema,
    TwitchMessage,
)


def test_send_message_schema():
    data = {'source': 'test_source', 'message': 'Hello, world!'}
    # Test deserialization
    result = SendMessageSchema().load(data)
    assert result.source == data['source']
    assert result.message == data['message']
    # Test serialization
    serialized = SendMessageSchema().dump(result)
    assert serialized == data


def test_twitch_message_schema():
    timestamp = datetime.now()
    data = {
        'content': 'Test message',
        'author': 'test_user',
        'channel': 'test_channel',
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'echo': False,
        'first': True,
        'id': '123',
    }
    result = TwitchMessageSchema().load(data)
    assert isinstance(result, TwitchMessage)
    assert result.content == data['content']
    assert result.author == data['author']
    assert result.channel == data['channel']
    assert result.timestamp.strftime('%Y-%m-%d %H:%M:%S') == data['timestamp']
    assert result.echo == data['echo']
    assert result.first == data['first']
    assert result.id == data['id']


def test_twitch_message_schema_from_mock():
    timestamp = datetime.now()
    mock_author = Mock()
    mock_author.name = 'test_user'
    mock_channel = Mock()
    mock_channel.name = 'test_channel'
    mock_message = Mock()
    mock_message.content = 'Test message'
    mock_message.channel = mock_channel
    mock_message.author = mock_author
    mock_message.timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    mock_message.echo = False
    mock_message.first = True
    mock_message.id = '123'
    result = TwitchMessageSchema().load(mock_message)
    assert isinstance(result, TwitchMessage)
    assert result.content == mock_message.content
    assert result.author == mock_author.name
    assert result.channel == mock_channel.name
    assert result.timestamp.strftime('%Y-%m-%d %H:%M:%S') == mock_message.timestamp
    assert result.echo == mock_message.echo
    assert result.first == mock_message.first
    assert result.id == mock_message.id


def test_twitch_message_schema_validation():
    with pytest.raises(
        ValidationError, match='Missing data for required field.'
    ) as exc_info:
        TwitchMessageSchema().load(None)
    assert 'content' in exc_info.value.messages
    assert 'Missing data for required field.' in exc_info.value.messages['content']
