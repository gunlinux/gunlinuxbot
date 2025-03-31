from marshmallow import Schema, fields, post_load
from typing import Any
import datetime

from gunlinuxbot.models.myqueue import QueueMessage


class QueueMessageSchema(Schema):
    event = fields.Str(required=True)
    timestamp = fields.DateTime(required=False, missing=datetime.datetime.now())
    data = fields.Str(required=True)
    source = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs: dict[Any, Any]) -> QueueMessage:
        _ = kwargs
        return QueueMessage(**data)
