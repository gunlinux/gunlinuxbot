from typing import Any, TypeVar, TypeAlias
from marshmallow import Schema, fields, post_load, pre_load
from datetime import datetime

from twitchio.message import Message
from gunlinuxbot.models.twitch import SendMessage, TwitchMessage

T = TypeVar('T', bound=Schema)
MessageData: TypeAlias = Message | dict[str, Any] | None


class SendMessageSchema(Schema):
    source = fields.Str(required=True)
    message = fields.Str(required=True)

    @post_load
    def make(self, data: dict[str, Any], **kwargs: dict[str, Any]) -> SendMessage:
        _ = kwargs
        return SendMessage(**data)


class TwitchMessageSchema(Schema):
    content = fields.Str(required=True)
    echo = fields.Bool(required=True)
    first = fields.Bool(required=True)
    id = fields.Str(required=True)
    channel = fields.Str()
    author = fields.Str()
    timestamp = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

    @post_load
    def make(self, data: dict[str, Any], **kwargs: dict[str, Any]) -> TwitchMessage:
        _ = kwargs
        return TwitchMessage(**data)

    @pre_load
    def load_from_message(
        self, data: MessageData, **kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        _ = kwargs
        if isinstance(data, dict):
            return data
        if data is None:
            return {}
        return {
            'timestamp': str(data.timestamp)
            if isinstance(data.timestamp, datetime)
            else data.timestamp,
            'content': data.content,
            'author': data.author.name,
            'channel': data.channel.name,
            'echo': data.echo,
            'first': data.first,
            'id': data.id,
        }
