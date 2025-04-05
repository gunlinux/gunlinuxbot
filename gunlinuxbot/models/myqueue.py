from dataclasses import dataclass


@dataclass
class QueueMessage:
    event: str
    data: str
    source: str = ''
