from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from gunlinuxbot.models.event import Event


@dataclass
class SendMessage:
    """
    Модель сообщения которое мы просто должны доставить на twitch
    """

    source: str
    message: str


@dataclass
class TwitchMessage(Event):
    """
    Модель входящего сообщения
    """

    content: str
    echo: bool
    first: bool
    id: str
    channel: str
    author: str
    timestamp: datetime

    def to_serializable_dict(self) -> dict[str, Any]:
        temp_dict = asdict(self)
        temp_dict['timestamp'] = self.timestamp.isoformat()
        return temp_dict
