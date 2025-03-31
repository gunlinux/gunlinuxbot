from dataclasses import dataclass

from enum import StrEnum


class DonationTypes(StrEnum):
    DONATION = '1'
    REWARD = '19'


class BillingSystem(StrEnum):
    FAKE = 'fake'
    TWITCH = 'TWITCH'


@dataclass
class AlertEvent:
    id: int
    alert_type: DonationTypes
    billing_system: BillingSystem
    username: str
    amount: float
    amount_formatted: str
    currency: str
    message: str
    # valdate as date???
    date_created: str
    _is_test_alert: bool
