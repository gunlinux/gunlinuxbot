from dataclasses import dataclass, asdict

import typing

from gunlinuxbot.models import Event


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

    def serialize(self) -> dict[str, typing.Any]:
        return asdict(self)
