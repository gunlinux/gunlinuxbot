import pytest
from dataclasses import asdict
from datetime import datetime
from unittest.mock import Mock
from marshmallow.exceptions import ValidationError

from gunlinuxbot.schemas.twitch import TwitchMessageSchema, SendMessageSchema
from gunlinuxbot.models.twitch import TwitchMessage, SendMessage


def test_send_message_schema():
    # Test serialization and deserialization of SendMessage
    data = {
        'source': 'test_source',
        'message': 'Hello, world!'
    }
    
    # Test deserialization
    result = SendMessageSchema().load(data)
    assert isinstance(result, SendMessage)
    assert result.source == data['source']
    assert result.message == data['message']
    
    # Test serialization
    serialized = SendMessageSchema().dump(result)
    assert serialized == data


def test_twitch_message_schema_dict():
    # Test with dictionary input
    data = {
        'content': 'Test message',
        'echo': False,
        'first': True,
        'id': '123',
        'channel': 'test_channel',
        'author': 'test_user',
        'timestamp': '2024-01-01 00:00:00'
    }
    
    result = TwitchMessageSchema().load(data)
    assert isinstance(result, TwitchMessage)
    assert result.content == data['content']
    assert result.echo == data['echo']
    assert result.first == data['first']
    assert result.id == data['id']
    assert result.channel == data['channel']
    assert result.author == data['author']
    assert result.timestamp == data['timestamp']


def test_twitch_message_schema_message():
    # Mock a TwitchIO Message object
    mock_author = Mock()
    mock_author.name = 'test_user'
    
    mock_channel = Mock()
    mock_channel.name = 'test_channel'
    
    mock_message = Mock()
    mock_message.content = 'Test message'
    mock_message.echo = False
    mock_message.first = True
    mock_message.id = '123'
    mock_message.channel = mock_channel
    mock_message.author = mock_author
    mock_message.timestamp = datetime.now()
    
    result = TwitchMessageSchema().load(mock_message)
    assert isinstance(result, TwitchMessage)
    assert result.content == mock_message.content
    assert result.echo == mock_message.echo
    assert result.first == mock_message.first
    assert result.id == mock_message.id
    assert result.channel == mock_message.channel.name
    assert result.author == mock_message.author.name
    assert result.timestamp == str(mock_message.timestamp)


def test_twitch_message_schema_none():
    # Test with None input - should raise ValidationError since content is required
    with pytest.raises(ValidationError) as exc_info:
        TwitchMessageSchema().load(None)
    assert 'content' in exc_info.value.messages
    assert 'Missing data for required field.' in exc_info.value.messages['content'] 