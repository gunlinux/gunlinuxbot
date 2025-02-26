from dataclasses import dataclass
from datetime import datetime


@dataclass
class QueueMessage:
    event: str
    data: str
    timestamp: datetime
    source: str = ''


