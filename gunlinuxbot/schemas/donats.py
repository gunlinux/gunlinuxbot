from marshmallow import Schema, fields, post_load, EXCLUDE
from typing import Any

from gunlinuxbot.models.donats import AlertEvent, DonationTypes, BillingSystem


class AlertEventSchema(Schema):
    id = fields.Int(required=True)
    alert_type = fields.Enum(DonationTypes, by_value=True)
    billing_system = fields.Enum(BillingSystem, by_value=True)
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

    @post_load
    def make(self, data: dict[str, Any], **kwargs: Any) -> AlertEvent:
        """Create an AlertEvent instance from deserialized data."""
        _ = kwargs
        return AlertEvent(**data)
