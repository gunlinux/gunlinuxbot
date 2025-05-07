from marshmallow import Schema, fields, post_load, EXCLUDE

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
    def make(self, data, **kwargs) -> AlertEvent:
        _ = kwargs
        return AlertEvent(**data)
