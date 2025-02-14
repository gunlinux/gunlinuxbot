from dataclasses import dataclass
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
    timestamp: str
