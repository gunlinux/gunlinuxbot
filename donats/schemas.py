import typing
from marshmallow import Schema, fields, post_load, EXCLUDE, pre_load
from donats.models import AlertEvent


class AlertEventSchema(Schema):
    id = fields.Int(required=True)
    alert_type = fields.Int(required=True)
    billing_system = fields.Str()
    username = fields.Str()
    amount = fields.Float()
    amount_formatted = fields.Str()
    currency = fields.Str()
    message = fields.Str()
    # valdate as date???
    date_created = fields.Str()
    _is_test_alert = fields.Bool()

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def preload(self, data: dict[str, typing.Any], **_) -> dict[str, typing.Any]:
        if 'alert_type' not in data:
            return data
        data['alert_type'] = (
            int(data['alert_type'])
            if isinstance(data['alert_type'], str)
            else data['alert_type']
        )
        return data

    @post_load
    def make(self, data: dict[str, typing.Any], **_) -> AlertEvent:
        return AlertEvent(**data)
