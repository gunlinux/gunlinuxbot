from dataclasses import dataclass
from enum import Enum
from typing import Any


class QueueMessageStatus(Enum):
    WAITING = 'waiting'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'


@dataclass
class QueueMessage:
    event: str
    data: str
    source: str = ''
    retry: int = 0
    status: QueueMessageStatus = QueueMessageStatus.WAITING

    def to_serializable_dict(self) -> dict[str, Any]:
        """Convert the message to a serializable dictionary."""
        return {
            'event': self.event,
            'data': self.data,
            'source': self.source,
            'retry': self.retry,
            'status': self.status.value,
        }
