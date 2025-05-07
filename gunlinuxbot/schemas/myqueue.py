from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField
from typing import Any

from gunlinuxbot.models.myqueue import QueueMessage, QueueMessageStatus


class QueueMessageSchema(Schema):
    event = fields.Str(required=True)
    data = fields.Str(required=True)
    source = fields.Str(required=False)
    retry = fields.Int(required=False)
    status = EnumField(
        QueueMessageStatus, by_value=True, dump_default=QueueMessageStatus.WAITING
    )

    @post_load
    def make(self, data, **kwargs: dict[Any, Any]) -> QueueMessage:
        _ = kwargs
        return QueueMessage(**data)
