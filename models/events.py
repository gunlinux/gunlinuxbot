from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    id_: int
    alert_type: str
    is_shown: str
    additional_data: dict
    billing_system: str
    billing_system_type: str
    username: str
    amount: str
    amount_formatted: str
    amount_main: int
    currency: str
    message: str
    header: str
    date_created: Any
    emotes: str
    ap_id: str
    _is_test_alert: bool
    message_type: str
    preset_id: int
    objects: dict
