import typing

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from requeue.models import QueueMessage, QueueMessageStatus


class QueueMessageSchema(Schema):
    event = fields.Str(required=True)
    data = fields.Str(required=True)
    source = fields.Str(required=False)
    retry = fields.Int(required=False)
    status = EnumField(
        QueueMessageStatus, by_value=True, dump_default=QueueMessageStatus.WAITING
    )

    @post_load
    def make(self, data: dict[str, typing.Any], **_: typing.Any) -> QueueMessage:
        return QueueMessage(**data)
