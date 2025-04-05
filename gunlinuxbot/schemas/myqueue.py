from marshmallow import Schema, fields, post_load
from typing import Any

from gunlinuxbot.models.myqueue import QueueMessage


class QueueMessageSchema(Schema):
    event = fields.Str(required=True)
    data = fields.Str(required=True)
    source = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs: dict[Any, Any]) -> QueueMessage:
        _ = kwargs
        return QueueMessage(**data)
