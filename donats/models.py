from dataclasses import dataclass

import typing

from gunlinuxbot.models import Event


"""
class DonationAlertTypes(Enum):
    DONATION = 1
    CUSTOM_REWARD = 19
    FOLLOW = 6


class DonationTypes(Enum):
    DONATION = '1'
    REWARD = '19'
"""


@dataclass
class AlertEvent(Event):
    id: int
    alert_type: int
    billing_system: str
    username: str | None
    amount: float
    amount_formatted: str
    currency: str
    message: str
    # valdate as date???
    date_created: str
    _is_test_alert: bool
    # Method to serialize the dataclass instance into JSON-compatible dict

    def serialize(self) -> dict[str, typing.Any]:
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'billing_system': self.billing_system,
            'username': self.username,
            'amount': self.amount,
            'amount_formatted': self.amount_formatted,
            'currency': self.currency,
            'message': self.message,
            'date_created': self.date_created,  # Assuming date is already in string format
            '_is_test_alert': self._is_test_alert,
        }
