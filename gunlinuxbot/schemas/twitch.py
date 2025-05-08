from typing import Any, TypeAlias
from marshmallow import Schema, fields, post_load, pre_load

from twitchio.message import Message
from gunlinuxbot.models.twitch import SendMessage, TwitchMessage

MessageData: TypeAlias = Message | dict[str, Any] | None


class SendMessageSchema(Schema):
    source = fields.Str(required=True)
    message = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs: dict[Any, Any]) -> SendMessage:
        _ = kwargs
        return SendMessage(**data)


class TwitchMessageSchema(Schema):
    content = fields.Str(required=True)
    echo = fields.Bool()
    first = fields.Bool()
    id = fields.Str()
    channel = fields.Str()
    author = fields.Str()
    timestamp = fields.Str()

    @post_load
    def make(self, data, **kwargs: dict[Any, Any]) -> TwitchMessage:
        _ = kwargs
        return TwitchMessage(**data)

    @pre_load
    def load_from_message(self, data: Message | dict | None, **kwargs) -> dict:
        _ = kwargs
        if isinstance(data, dict):
            return data
        if data is None:
            return {}
        return {
            'timestamp': str(data.timestamp),
            'content': data.content,
            'author': data.author.name,
            'channel': data.channel.name,
            'echo': data.echo,
            'first': data.first,
            'id': data.id,
        }
