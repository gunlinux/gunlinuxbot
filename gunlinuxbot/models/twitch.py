from dataclasses import dataclass


@dataclass
class SendMessage:
    """
    Модель сообщения которое мы просто должны доставить на twitch
    """
    source: str
    message: str


@dataclass
class TwitchMessage:
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
