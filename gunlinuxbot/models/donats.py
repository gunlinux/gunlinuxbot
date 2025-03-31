from dataclasses import dataclass

from enum import Enum

from gunlinuxbot.models.event import Event


class DonationTypes(Enum):
    DONATION = '1'
    REWARD = '19'


class BillingSystem(Enum):
    FAKE = 'fake'
    TWITCH = 'TWITCH'


@dataclass
class AlertEvent(Event):
    id: int
    alert_type: DonationTypes
    billing_system: BillingSystem
    username: str | None
    amount: float
    amount_formatted: str
    currency: str
    message: str
    # valdate as date???
    date_created: str
    _is_test_alert: bool
